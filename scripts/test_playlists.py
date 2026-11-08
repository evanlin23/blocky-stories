"""Offline tests for scripts/playlists.py: a fake YouTube client, no network, no secrets."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import playlists as pl  # noqa: E402


class Req:
    def __init__(self, out):
        self.out = out

    def execute(self):
        if isinstance(self.out, Exception):
            raise self.out
        return self.out


class FakeYT:
    def __init__(self, fail_items=False):
        self.made, self.items, self.fail_items = [], [], fail_items

    def playlists(self):
        yt = self

        class P:
            def insert(self, part, body):
                yt.made.append(body["snippet"]["title"])
                return Req({"id": f"PL{len(yt.made)}"})
        return P()

    def playlistItems(self):  # noqa: N802 (the API's own name)
        yt = self

        class I:
            def insert(self, part, body):
                if yt.fail_items:
                    return Req(RuntimeError("quota"))
                yt.items.append((body["snippet"]["playlistId"], body["snippet"]["resourceId"]["videoId"]))
                return Req({})
        return I()


def test_keys_for_lane():
    assert pl.keys_for({"lane": "core"}) == ["all"]
    assert pl.keys_for({"lane": "interactive"}) == ["all", "interactive"]
    assert pl.keys_for(None) == ["all"]


def test_add_makes_each_playlist_once(tmp_path, monkeypatch):
    monkeypatch.setattr(pl, "FILE", tmp_path / "playlists.json")
    yt = FakeYT()
    assert pl.add(yt, "v1", ["all", "interactive"]) == []
    assert pl.add(yt, "v2", ["all"]) == []
    assert yt.made == [pl.PLAYLISTS["all"][0], pl.PLAYLISTS["interactive"][0]]   # "all" made once
    assert yt.items == [("PL1", "v1"), ("PL2", "v1"), ("PL1", "v2")]
    assert json.loads((tmp_path / "playlists.json").read_text()) == {"all": "PL1", "interactive": "PL2"}


def test_add_never_raises_and_reports(tmp_path, monkeypatch):
    monkeypatch.setattr(pl, "FILE", tmp_path / "playlists.json")
    assert pl.add(FakeYT(fail_items=True), "v1", ["all"]) == ["all"]


def test_owner_steps_names_newest_compilation(tmp_path, monkeypatch):
    comps = tmp_path / "compilations.json"
    comps.write_text(json.dumps({"2026-11-08": {"video_id": "old"}, "2026-11-15": {"video_id": "new"}}))
    monkeypatch.setattr(pl, "COMPILATIONS", comps)
    steps = pl.owner_steps(["interactive"])
    assert "watch?v=new" in steps and "Related video" in steps and pl.PLAYLISTS["interactive"][0] in steps
    monkeypatch.setattr(pl, "COMPILATIONS", tmp_path / "none.json")
    assert pl.owner_steps([]) == ""
