"""The polish pack (opt-in per story with `"look": {"polish": true}`; meant to become the default for new stories).

Only moves the research and our own previews back (docs/research/playbook.md, docs/research/polish-pack.md):

Sound (sound.py calls `sound_events` and `bed`):
- a soft whoosh, low-passed under 4 kHz, on hard cuts (at most one every `whoosh_gap` s) and on every punch-in
- a low hit on emphasised lines (the punch-ins) and a fuller one on reveals (big pause words, `polish.reveal`)
- a riser into every `music_drops` hole (it ends where the silence starts) and into `polish.twist`
- a room-tone or ambience bed from assets/ under the whole film, so nothing is ever digital silence (a drop only
  takes it down `bed_drop_db`, not 40 dB)
- doors, latches, creaks and thuds placed from the builder's marks: an acting key with `"sfx": "door"` (panned to
  where the character stands), or a cue whose name starts with `door`, `latch`, `creak` or `thud`
- the voice on top: the bed, the polish effects, the ambience and the music duck under the narrator (sidechain)
  The master is unchanged: -14 LUFS, true peak under -1 dBTP on the encoded file.

Captions (post.py): a quick pop-in, 90 to 100% over 80 ms, with the key word in the story's colour as before.

Motion (post.py, on the output crop, so it is smooth even when the drawings are on twos or fours):
- a punch-in of `punch` (default 6%) eased over 0.12 s on emphasised lines, held to the cut
- a slow drift (zoom and pan, `drift` default 3% over a shot) on every shot over 1.5 s whose camera doesn't move,
  so no picture is ever still
- an optional gentle handheld sway (`sway`: a list of shot ids, or true for every shot), slow sines, no jitter

Picture (post.py): a bright grade preset that lifts shadows instead of crushing them, a soft vignette and light
grain (it caps the story's vignette and grain and raises its exposure floor; the story's colours stay).

Every motion is a slow ease, so `python -m blocky flash` reads it as no change.

`look.polish` is `true` or a dict that overrides any of DEFAULTS, e.g.
    "look": {"polish": {"sway": ["S12", "S13"], "emph": ["L03.1", "L19"], "reveal": ["L38"], "twist": "L34"}}
"""

from __future__ import annotations

import math

DEFAULTS = {
    # sound
    "whoosh": True, "whoosh_db": -19.0, "whoosh_gap": 1.4, "whoosh_lp": 3000.0,
    "hits": True, "hit_db": -17.0, "reveal_db": -11.0,
    "riser": True, "riser_db": -15.0, "riser_dur": 1.8,
    "bed": True, "bed_kind": None, "bed_lufs": -44.0, "bed_drop_db": -12.0,
    "marks": True, "mark_db": -14.0,
    "duck": True, "duck_db": 6.0,
    # captions
    "pop": True,
    # motion
    "punch": 0.06, "punch_gap": 2.4, "fill": 2.2, "drift": 0.03, "drift_min": 1.5, "sway": False, "sway_amp": 0.004,
    # picture
    "grade": "bright",
    # builder marks
    "emph": None, "auto": True, "reveal": [], "twist": None, "quiet": [],
}
GRADES = {
    # lift: a toe that raises the darkest tones (out + lift * (1 - out)^3), so shadows keep their detail on a TV
    "bright": {"exposure_min": 1.04, "saturation_min": 1.06, "contrast_max": 1.05, "vignette_max": 0.2,
               "grain_max": 0.009, "lift": 0.035},
    "none": {},
}
MARK_SFX = ("door", "latch", "creak", "thud", "knock")
SEP = 0.25          # a polish sound never lands this close to one the builder placed


def spec(st: dict) -> dict | None:
    """The story's polish settings, or None when it's off."""
    p = (st.get("look") or {}).get("polish")
    if not p:
        return None
    return {**DEFAULTS, **(p if isinstance(p, dict) else {})}


# ------------------------------------------------------------------------------------------------ marks

def _is_key(word: str) -> bool:
    core = "".join(ch for ch in word if ch.isalnum())
    return bool(core) and (core.isupper() and len(core) > 1 or core.isdigit())


def on_key(tl: dict, t: float) -> float:
    """A time on a chunk's first word, moved to its key word (the first word in CAPS), estimated by the letters
    before it: "was MUM." lands on MUM, not "was" (critic, ep32 A/B)."""
    for ln in tl["lines"].values():
        for a, b, text in ln["chunks"]:
            if abs(a - t) < 0.02:
                words = text.split()
                k = next((i for i, w in enumerate(words) if _is_key(w)), 0)
                before = len(" ".join(words[:k])) + (1 if k else 0)
                return a + (b - a) * before / max(1, len(text))
    return t


def emph_times(tl: dict, p: dict, at=None) -> list[float]:
    """When the punch-ins and key-word hits land, each on its key word: the builder's `emph` refs, plus (with
    `auto`, the default, or with no refs) every big pause word and every caption whose words are all key words
    ("SIX.", "BACK ROW") and the first caption (the hook). Then a fill punch in any shot over `fill` s that has
    none, on the caption nearest its middle, so something changes every 1 to 2 s. At most one per `punch_gap` s
    (the builder's own refs always count), so it never pumps."""
    if at is None:
        from blocky.timeline import resolver
        at = resolver(tl["lines"], tl["duration"])
    mine = sorted(on_key(tl, at(r)) for r in (p.get("emph") or []))
    auto = []
    if p.get("auto", True) or p.get("emph") is None:
        caps = tl["captions"]
        auto = [on_key(tl, c["start"] + 0.04) if not c.get("big") else c["start"] + 0.04 for i, c in enumerate(caps)
                if i == 0 or c.get("big") or all(_is_key(w) for w in c["text"].split())]
    quiet = [at(r) for r in p.get("quiet") or []]
    out = list(mine)
    for t in sorted(auto):
        if all(abs(t - u) >= p["punch_gap"] for u in out) and all(abs(t - q) > 0.5 for q in quiet):
            out.append(t)
    if p.get("fill"):
        caps = tl["captions"]
        for s in tl["shots"]:
            if s["end"] - s["start"] < p["fill"] or any(s["start"] <= t < s["end"] for t in out):
                continue
            mid = (s["start"] + s["end"]) / 2
            cs = [on_key(tl, c["start"] + 0.04) for c in caps if s["start"] + 0.8 <= c["start"] <= s["end"] - 0.6]
            if cs:
                t = min(cs, key=lambda x: abs(x - mid))
                if all(abs(t - u) >= 1.0 for u in out):
                    out.append(t)
    return sorted(out)


def reveal_times(tl: dict, p: dict, at) -> list[float]:
    """Reveals: the builder's `reveal` refs, and every big pause word (THUD, KNOCK) that has words."""
    ts = [on_key(tl, at(r)) for r in p.get("reveal") or []]
    ts += [c[0] for ln in tl["lines"].values() if ln["who"] == "pause" for c in ln["chunks"] if c[2].strip()]
    return sorted(set(round(t, 3) for t in ts))


def cut_times(tl: dict) -> list[float]:
    return [s["start"] for s in tl["shots"][1:]]


# ------------------------------------------------------------------------------------------------ sound

def sound_events(tl: dict, st: dict, p: dict, at) -> list[dict]:
    """The polish pack's sounds as sfx-like entries {t, kind, db, pan, lp, dur}, kept clear of the builder's own."""
    snd = st.get("sound", {})
    taken = [at(e["at"]) for e in snd.get("sfx", [])]
    clear = lambda t, gap=SEP: all(abs(t - u) >= gap for u in taken)
    ev = []
    dur = tl["duration"]
    emph = emph_times(tl, p, at)
    if p["whoosh"]:
        last = -9.0
        # every punch-in, and the cuts that fall between lines (never under a word), at most one per whoosh_gap
        # (a whoosh leads its cut by 0.12 s)
        onsets = [ln["onset"] for ln in tl["lines"].values()]
        cuts = [t for t in cut_times(tl) if any(abs(t - o) < 0.06 for o in onsets)]
        for t in sorted(set(emph) | set(cuts)):
            forced = t in emph
            if (forced or t - last >= p["whoosh_gap"]) and clear(t) and 0.3 < t < dur - 0.3:
                ev.append({"t": t - 0.12, "kind": "whoosh", "db": p["whoosh_db"] + (1.5 if forced else 0.0),
                           "lp": p["whoosh_lp"], "pan": 0.0})
                last = t
    if p["hits"]:
        rev = reveal_times(tl, p, at)
        for t in rev:
            if clear(t):
                ev.append({"t": t, "kind": "hit", "db": p["reveal_db"], "lp": 3800.0, "pan": 0.0})
        quiet = [at(r) for r in p.get("quiet") or []]   # the builder's "no hit here" (a warm line)
        for t in emph:
            if clear(t) and all(abs(t - u) >= SEP for u in rev) and all(abs(t - q) > 0.5 for q in quiet):
                ev.append({"t": t, "kind": "lowhit", "db": p["hit_db"], "lp": 1200.0, "pan": 0.0})
    if p["riser"]:
        from blocky.sound import drop_spec
        ends = [at(drop_spec(d)["from"]) for d in snd.get("music_drops", [])]
        if p.get("twist"):
            ends.append(at(p["twist"]))
        for e in sorted(set(ends)):
            d = min(p["riser_dur"], e - 0.2)
            # skip a riser where the builder already put one in the run-up
            if d > 0.5 and not any(x.get("kind") == "riser" and e - d - 0.6 <= at(x["at"]) <= e
                                   for x in snd.get("sfx", [])):
                ev.append({"t": e - d, "kind": "riser", "db": p["riser_db"], "dur": d, "lp": 3800.0, "pan": 0.0})
    if p["marks"]:
        for who, keys in tl.get("acting", {}).items():
            for k in keys:
                kind = k.get("sfx")
                if kind in MARK_SFX and clear(k["t"], 0.15):
                    pos = k.get("pos") or [0, 0]
                    ev.append({"t": k["t"], "kind": kind, "db": float(k.get("sfx_db", p["mark_db"])),
                               "pan": max(-0.6, min(0.6, float(pos[0]) * 0.1)), "lp": 4000.0})
        for c in tl.get("cues", []):
            kind = next((m for m in MARK_SFX if c["name"].startswith(m)), None)
            if kind and clear(c["t"], 0.15):
                ev.append({"t": c["t"], "kind": kind, "db": p["mark_db"], "pan": 0.0, "lp": 4000.0})
    return sorted(ev, key=lambda e: e["t"])


def bed_kind(st: dict, p: dict) -> str:
    """The bed: the builder's `bed_kind`, else the recorded ambience the story uses most, else room tone."""
    if p.get("bed_kind"):
        return p["bed_kind"]
    from blocky.sound import AMB_SAMPLES
    kinds = [a["kind"] for a in st.get("sound", {}).get("ambience", []) if a["kind"] in AMB_SAMPLES]
    return max(set(kinds), key=kinds.count) if kinds else "room"


# ------------------------------------------------------------------------------------------------ motion

def _ease(u: float) -> float:
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def _static(shot_spec: dict | None) -> bool:
    if not shot_spec:
        return True
    cam = shot_spec.get("cam") or []
    if shot_spec.get("follow"):
        return False
    return len(cam) <= 1 or all(c[1:] == cam[0][1:] for c in cam)


def motion(tl: dict, st: dict, p: dict, t: float, emph: list[float] | None = None) -> tuple[float, float, float]:
    """The pack's camera move at time t, on the output crop: (zoom, dx, dy), dx and dy as fractions of the frame."""
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    k = tl["shots"].index(shot)
    sspec = next((s for s in st.get("shots", []) if s["id"] == shot["id"]), None)
    length = shot["end"] - shot["start"]
    u = (t - shot["start"]) / max(1e-6, length)
    zoom, dx, dy = 1.0, 0.0, 0.0
    if p["drift"] and length >= p["drift_min"] and _static(sspec):
        # alternate in and out shot to shot, with a slow sideways slide, eased at both ends of the shot
        e = _ease(u) * 0.7 + u * 0.3
        d = p["drift"]
        zoom = 1 + d * (e if k % 2 == 0 else 1 - e) + d * 0.2
        side = 1 if (k // 2) % 2 == 0 else -1
        dx = side * d * 0.15 * (e - 0.5)
    if p["punch"]:
        for te in emph if emph is not None else emph_times(tl, p):
            if shot["start"] - 1e-6 <= te < shot["end"] and t >= te:
                # held to the cut (no zoom back out mid-shot), at most 2.5 s, then it eases back over 0.4 s
                x = t - te
                amt = _ease(x / 0.12) * (1 - _ease((x - 2.5) / 0.4))
                zoom *= 1 + p["punch"] * amt
    sway = p.get("sway")
    if sway and (sway is True or shot["id"] in sway):
        a = p["sway_amp"]
        dx += a * (math.sin(t * 2 * math.pi * 0.31 + 1.3) + 0.5 * math.sin(t * 2 * math.pi * 0.53))
        dy += a * 0.7 * (math.sin(t * 2 * math.pi * 0.23 + 0.4) + 0.4 * math.sin(t * 2 * math.pi * 0.47 + 2.0))
    return zoom, dx, dy


# ------------------------------------------------------------------------------------------------ picture

def grade(g: dict, p: dict) -> dict:
    """The story's grade with the preset's floors and caps applied (its own tints and colours kept)."""
    pr = GRADES.get(p.get("grade") or "none", {})
    if not pr:
        return g
    out = dict(g)
    out["exposure"] = max(g.get("exposure", 1.0), pr["exposure_min"])
    out["saturation"] = max(g.get("saturation", 1.0), pr["saturation_min"])
    out["contrast"] = min(g.get("contrast", 1.05), pr["contrast_max"])
    out["vignette"] = min(g.get("vignette", 0.35), pr["vignette_max"])
    out["grain"] = min(g.get("grain", 0.012), pr["grain_max"])
    out["lift"] = max(g.get("lift", 0.0), pr["lift"])
    return out


def caption_scale(x: float) -> float:
    """The polish caption pop: 90% to 100% over 80 ms, eased out (x = seconds since the caption appeared)."""
    if x >= 0.08:
        return 1.0
    u = max(0.0, x) / 0.08
    return 0.9 + 0.1 * (1 - (1 - u) ** 3)
