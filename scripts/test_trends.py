"""Offline tests for scripts/trends.py's two query sets: a fake YouTube client, no network, no secrets."""

import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import trends  # noqa: E402

NOW = dt.datetime(2026, 11, 9, 12, tzinfo=dt.timezone.utc)


class Exec:
    def __init__(self, v):
        self.v = v

    def execute(self):
        return self.v


class FakeYT:
    def __init__(self):
        self.searches = []

    def search(self):
        outer = self

        class S:
            def list(self, q, **kw):
                outer.searches.append(q)
                n = abs(hash(q)) % 5 + 3
                return Exec({"items": [{"id": {"videoId": f"{q[:6]}-{i}"}} for i in range(n)] +
                             [{"id": {"videoId": "shared"}}]})
        return S()

    def videos(self):
        class V:
            def list(self, id, **kw):
                assert "status" in kw["part"]
                out = []
                for i, vid in enumerate(id.split(",")):
                    out.append({"id": vid, "snippet": {"title": f"T {vid}", "channelTitle": f"ch{i % 4}",
                                                       "channelId": f"C{i % 4}", "publishedAt": "2026-11-05T10:00:00Z"},
                                "statistics": {"viewCount": str(100_000 * (i + 1))},
                                "contentDetails": {"duration": "PT45S" if i % 7 else "PT5M"},
                                "status": {"madeForKids": i % 3 == 0}})
                return Exec({"items": out})
        return V()

    def channels(self):
        class C:
            def list(self, id, **kw):
                return Exec({"items": [{"id": c, "snippet": {"publishedAt": "2026-08-01T00:00:00Z" if c == "C0"
                                                             else "2019-01-01T00:00:00Z"},
                                        "statistics": {"subscriberCount": "5000"}} for c in id.split(",")]})
        return C()


def test_wide_set_is_separate_and_counted():
    assert not set(trends.QUERIES) & set(trends.QUERIES_WIDE)
    assert len(trends.QUERIES_WIDE) == 12
    yt = FakeYT()
    rows = trends.scan(yt, NOW, trends.QUERIES_WIDE)
    assert yt.searches == list(trends.QUERIES_WIDE.values())
    assert all(r["seconds"] <= 180 for r in rows)          # Shorts only
    shared = next(r for r in rows if r["id"] == "shared")
    assert len(shared["queries"]) == 12                    # one video found by every query keeps all its formats
    mom = trends.momentum(rows, trends.QUERIES_WIDE)
    assert set(mom) == set(trends.QUERIES_WIDE)


def test_channels_and_summary():
    yt = FakeYT()
    rows = trends.scan(yt, NOW, trends.QUERIES_WIDE)
    trends.channels(yt, rows, NOW)
    assert {r["channel_age_days"] for r in rows if r["channel_id"] == "C0"} == {100}
    summ = trends.wide_summary(rows)
    assert len(summ) == 12 and summ == sorted(summ, key=lambda x: -x["median_per_day"])
    x = summ[0]
    assert x["new_channels"] <= x["channels"] and "/" in x["made_for_kids"]
    md = trends.report_wide(rows, trends.momentum(rows, trends.QUERIES_WIDE), None)
    assert "Outside the niche" in md and "Fastest 25 outside the niche" in md


def test_blocky_momentum_unchanged_by_default():
    rows = [{"per_day": 10, "queries": ["comedy"]}, {"per_day": 30, "queries": ["comedy"]}]
    mom = trends.momentum(rows)
    assert set(mom) == set(trends.QUERIES) and mom["comedy"] == 20
