"""Offline tests for scripts/brand_scan.py."""

import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import brand_scan as bs  # noqa: E402

NOW = dt.datetime(2026, 11, 3, tzinfo=dt.timezone.utc)


class Ex:
    def __init__(self, v):
        self.v = v

    def execute(self):
        return self.v


class YT:
    def channels(self):
        class C:
            def list(self, id, **kw):
                return Ex({"items": [{"id": c, "snippet": {"title": f"Chan {c}", "customUrl": f"@chan{c.lower()}",
                                                           "description": "x " * 400, "publishedAt": "2026-10-01T00:00:00Z"},
                                      "statistics": {"subscriberCount": "1200"},
                                      "brandingSettings": {"image": {"bannerExternalUrl": "u"} if c == "A" else {}}}
                                     for c in id.split(",")]})
        return C()

    def playlists(self):
        class P:
            def list(self, channelId, **kw):
                return Ex({"items": [{"snippet": {"title": "Town rules"}, "contentDetails": {"itemCount": 9}}]})
        return P()

    def search(self):
        class S:
            def list(self, q, **kw):
                return Ex({"items": [{"id": {"channelId": "A"}, "snippet": {"channelTitle": "Chan A"}},
                                     {"id": {"channelId": "B"}, "snippet": {"channelTitle": "Other"}}]})
        return S()


def test_pick_channels_dedupes_and_filters():
    scan = {"rows": [{"channel": "G", "channel_id": "g1"}, {"channel": "H", "channel_id": "h1"}],
            "rows_wide": [{"channel_id": "n1", "channel_age_days": 20, "per_day": 200_000},
                          {"channel_id": "o1", "channel_age_days": 2000, "per_day": 900_000},
                          {"channel_id": "s1", "channel_age_days": 20, "per_day": 5}]}
    deep = {"videos": [{"channel": "G"}, {"channel": "G"}, {"channel": "H"}]}
    assert bs.pick_channels(scan, deep) == ["g1", "h1", "n1"]


def test_rows_names_and_budget():
    b = bs.Budget()
    rows = bs.channel_rows(YT(), ["A", "B"], NOW, b)
    assert [r["banner"] for r in rows] == [True, False] and rows[0]["age_days"] == 33
    assert len(rows[0]["description"]) <= 300
    assert bs.playlists(YT(), "A", b)[0]["items"] == 9
    c = bs.name_check(YT(), "chan a", b)
    assert [h["title"] for h in c["exact"]] == ["Chan A"]
    assert b.used == 1 + 1 + 100 + 1
    assert bs.Budget(cap=50).spend("search.list") is False
    md = bs.report(rows, [c], "2026-11-03", b.used)
    assert "Candidate names" in md and "Chan A (1200)" in md
