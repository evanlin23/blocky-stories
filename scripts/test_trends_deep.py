"""Offline tests for scripts/trends_deep.py: a fake YouTube client, no network, no secrets."""

import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import trends_deep as td  # noqa: E402

NOW = dt.datetime(2026, 11, 9, 12, tzinfo=dt.timezone.utc)


class Call:
    def __init__(self, fn, log, name):
        self.fn, self.log, self.name = fn, log, name

    def list(self, **kw):
        self.log.append((self.name, kw))
        fn = self.fn

        class R:
            def execute(self):
                return fn(**kw)
        return R()


class FakeYT:
    def __init__(self, n=45, disabled=()):
        self.log, self.n, self.disabled = [], n, set(disabled)

    def videos(self):
        def f(id, **_):
            return {"items": [{"id": i, "snippet": {
                "title": f"Title {i}", "channelTitle": "Chan", "channelId": f"C{int(i[1:]) % 3}",
                "publishedAt": "2026-11-05T17:30:00Z", "tags": ["roblox", "story"],
                "description": f"In this town @someone made a rule https://x.y/z\nsecond line {i}"},
                "statistics": {"viewCount": "1000", "likeCount": "50", "commentCount": "4"}}
                for i in id.split(",")]}
        return Call(f, self.log, "videos")

    def channels(self):
        def f(id, **_):
            out = []
            for c in id.split(","):
                st = {"subscriberCount": "12000", "videoCount": "30"}
                if c == "C2":
                    st = {"hiddenSubscriberCount": True, "videoCount": "3"}
                out.append({"id": c, "snippet": {"publishedAt": "2026-10-10T00:00:00Z"}, "statistics": st})
            return {"items": out}
        return Call(f, self.log, "channels")

    def commentThreads(self):
        def f(videoId, **_):
            if videoId in self.disabled:
                raise RuntimeError("commentsDisabled")
            return {"items": [{"snippet": {"topLevelComment": {"snippet": {
                "textOriginal": f"@Fan{k} the ending got me " + "x" * (300 if k == 0 else 1),
                "authorDisplayName": "SECRET_NAME"}}}} for k in range(20)]}
        return Call(f, self.log, "commentThreads")


def rows(n=45):
    return [{"id": f"v{i}", "title": f"Title v{i}", "views": 1000, "seconds": 60 + i, "per_day": 1000 - i,
             "queries": ["rule premise"], "published": "2026-11-05T17:30:00Z"} for i in range(n)]


def test_takes_the_40_fastest_and_counts_units():
    yt, b = FakeYT(), td.Budget()
    items = td.deep(yt, list(reversed(rows())), NOW, b)
    assert [x["id"] for x in items] == [f"v{i}" for i in range(40)]
    # one videos.list, one channels.list, 40 commentThreads.list
    assert b.used == 42 and b.calls == {"videos.list": 1, "channels.list": 1, "commentThreads.list": 40}
    assert [n for n, _ in yt.log].count("commentThreads") == 40
    kw = next(k for n, k in yt.log if n == "commentThreads")
    assert kw["order"] == "relevance" and kw["maxResults"] == 20


def test_fields_ratios_and_privacy():
    items = td.deep(FakeYT(), rows(), NOW, td.Budget())
    x = items[0]
    assert x["hour_utc"] == 17 and x["weekday"] == "Thu"
    assert x["like_per_view"] == 0.05 and x["comment_per_view"] == 0.004
    assert x["channel_age_days"] == 30 and x["tags"] == ["roblox", "story"]
    assert len(x["top_comments"]) == 20
    blob = repr(items)
    assert "SECRET_NAME" not in blob and "@Fan" not in blob and "@someone" not in blob
    assert "https://" not in blob
    assert all(len(c) <= td.COMMENT_CHARS for c in x["top_comments"])
    assert x["description_first_line"].startswith("In this town @user")
    hidden = [i for i in items if i["channel_subscribers"] is None]
    assert hidden and all(i["channel_videos"] == 3 for i in hidden)


def test_comments_off_does_not_stop_the_run():
    items = td.deep(FakeYT(disabled={"v1"}), rows(), NOW, td.Budget())
    assert items[1]["top_comments"] == [] and "unavailable" in items[1]["comments_note"]
    assert len(items[2]["top_comments"]) == 20


def test_cap_is_never_exceeded():
    b = td.Budget(cap=10)
    items = td.deep(FakeYT(), rows(), NOW, b)
    assert b.used == 10 and len(items) == 40
    assert sum(1 for x in items if x["comments_note"] == "skipped: unit cap") == 32


def test_daily_total_stays_far_under_the_free_quota():
    from trends import QUERIES, QUERIES_WIDE
    scan = td.scan_cost(250 + 300, len(QUERIES) + len(QUERIES_WIDE)) + 6   # trends.py worst case, both sets + channels
    assert scan == 2217
    assert scan + td.CAP < 10_000 - 1_700        # leaves the daily upload its ~1,600


def test_report_renders():
    b = td.Budget()
    items = td.deep(FakeYT(), rows(), NOW, b)
    md = td.report(items, "2026-11-09", {"scan": 1004, "deep": b.used, "calls": "x"})
    assert "# Deep trend data 2026-11-09" in md and "| 40 |" in md and "hidden" in md
    assert "ending" in md   # comment word counts
