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
    "whoosh": True, "whoosh_cuts": False, "whoosh_db": -19.0, "whoosh_gap": 1.4, "whoosh_lp": 3000.0,
    "hits": True, "key_hits": "hook", "hit_db": -17.0, "reveal_db": -11.0, "music_bed": True,
    "riser": True, "riser_db": -15.0, "riser_dur": 1.8, "riser_gap": 15.0,
    "bed": True, "bed_kind": None, "bed_lufs": -44.0, "bed_drop_db": -12.0,
    "marks": True, "mark_db": -14.0,
    "duck": True, "duck_db": 8.0, "music_duck_db": "auto", "voice_gap_db": 10.5,
    # captions
    "pop": True,
    # motion
    "push": 0.12, "reframe_every": 0.8, "reframe_min": 1.6, "reframe_zoom": 1.12, "max_zoom": 1.18,
    "punch": 0.06, "punch_gap": 2.4, "punch_rate": 0.7, "fill": 0.0, "hit_gap": 4.0, "drift": 0.03,
    "ones": "moving", "camera": True, "cam_push": 0.07, "cam_arc": 3.0, "ease": True, "idle": True, "idle_scale": 1.0, "drift_min": 1.5, "sway": False, "sway_amp": 0.004,
    # picture
    "grade": "bright",
    # builder marks
    "emph": None, "auto": True, "reveal": [], "twist": None, "quiet": [],
    "punch_cap": {},     # opt-in: {shot id: most the punch-in may zoom there} (a head that must stay in frame)
}
GRADES = {
    # lift: a toe that raises the darkest tones (out + lift * (1 - out)^3), so shadows keep their detail on a TV
    "bright": {"exposure_min": 1.12, "red_line": 0.78, "saturation_min": 1.1, "contrast_max": 1.05, "vignette_max": 0.2,
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


def quiet_spans(p: dict, at) -> list[tuple[float, float]]:
    """The builder's `quiet` marks: a ref keeps a hit off that word (0.5 s either side); a [from, to] pair keeps
    every polish whoosh, hit and added punch-in out of a span (a warm beat that should stay still)."""
    out = []
    for q in p.get("quiet") or []:
        if isinstance(q, (list, tuple)):
            out.append((at(q[0]), at(q[1])))
        else:
            t = at(q)
            out.append((t - 0.5, t + 0.5))
    return out


def _in(t: float, spans) -> bool:
    return any(a <= t <= b for a, b in spans)


def key_times(tl: dict, p: dict, at) -> list[tuple[int, float]]:
    """Every key-word moment as (priority, time), on its key word: the builder's `emph` refs (0), the hook (1),
    big pause words (2), and with `auto` (the default, or with no refs) every caption whose words are all key words
    (3: "SIX.", "BACK ROW"). Quiet spans removed."""
    quiet = quiet_spans(p, at)
    out = [(0, on_key(tl, at(r))) for r in (p.get("emph") or [])]
    caps = tl["captions"]
    if caps:
        out.append((1, on_key(tl, caps[0]["start"] + 0.04)))
    out += [(2, c["start"] + 0.04) for c in caps if c.get("big")]
    if p.get("auto", True) or p.get("emph") is None:
        out += [(3, on_key(tl, c["start"] + 0.04)) for c in caps[1:]
                if not c.get("big") and all(_is_key(w) for w in c["text"].split())]
        # 4: a key word that ends its line (the line's last chunk): where the voice lands the stress
        last = {ln["chunks"][-1][0] for ln in tl["lines"].values() if ln["who"] != "pause" and ln["chunks"]}
        out += [(4, on_key(tl, c["start"] + 0.04)) for c in caps[1:] if not c.get("big")
                and any(abs(c["start"] + 0.04 - a) < 0.03 for a in last) and any(_is_key(w) for w in c["text"].split())]
    return sorted((k, t) for k, t in out if not _in(t, quiet))


def _spaced(cands, gap, cap=None):
    out = []
    for _k, t in cands:   # by priority, then time
        if (cap is None or len(out) < cap) and all(abs(t - u) >= gap for u in out):
            out.append(t)
    return sorted(out)


def hit_times(tl: dict, p: dict, at) -> list[float]:
    """The low hits: every key-word moment, at least `hit_gap` s apart (the critic, ep32: spaced 4 s, they help)."""
    return _spaced(key_times(tl, p, at), p.get("hit_gap", 4.0))


def emph_times(tl: dict, p: dict, at=None) -> list[float]:
    """The punch-ins, on key words only: the builder's `emph` refs first, then the hook, big words and all-caps
    captions, at most `punch_rate` per 10 s and evenly spread (craft metrics, 2026-11-03: 2.1 per 10 s was five times
    back-row's 0.44). An optional `fill` adds one in any shot over `fill` s that has none (off by default: the
    camera moves now keep long shots alive)."""
    if at is None:
        from blocky.timeline import resolver
        at = resolver(tl["lines"], tl["duration"])
    quiet = quiet_spans(p, at)
    rate = p.get("punch_rate")
    cap = max(1, int(rate * tl["duration"] / 10 + 0.5)) if rate else None
    gap = max(p["punch_gap"], 5.0 / rate) if rate else p["punch_gap"]
    out = _spaced(key_times(tl, p, at), gap, cap)
    if p.get("fill"):
        caps = tl["captions"]
        for s in tl["shots"]:
            if s["end"] - s["start"] < p["fill"] or any(s["start"] <= t < s["end"] for t in out):
                continue
            mid = (s["start"] + s["end"]) / 2
            cs = [on_key(tl, c["start"] + 0.04) for c in caps if s["start"] + 0.8 <= c["start"] <= s["end"] - 0.6]
            if cs:
                t = min(cs, key=lambda x: abs(x - mid))
                if all(abs(t - u) >= 1.0 for u in out) and not _in(t, quiet):
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
    quiet = quiet_spans(p, at)
    spans = [q for q in quiet if q[1] - q[0] > 1.0 + 1e-6]   # whole spans keep whooshes out too
    if p["whoosh"]:
        last = -9.0
        # every punch-in, and the cuts that fall between lines (never under a word), at most one per whoosh_gap
        # (a whoosh leads its cut by 0.12 s)
        onsets = [ln["onset"] for ln in tl["lines"].values()]
        # v2.2 (owner, 2026-11-03: the hits use few effects): cuts only with whoosh_cuts; punch-ins always
        cuts = [t for t in cut_times(tl) if any(abs(t - o) < 0.06 for o in onsets)] if p.get("whoosh_cuts") else []
        for t in sorted(set(emph) | set(cuts)):
            forced = t in emph
            if (forced or t - last >= p["whoosh_gap"]) and clear(t) and 0.3 < t < dur - 0.3 and not _in(t, spans):
                ev.append({"t": t - 0.12, "kind": "whoosh", "db": p["whoosh_db"] + (1.5 if forced else 0.0),
                           "lp": p["whoosh_lp"], "pan": 0.0})
                last = t
    if p["hits"]:
        rev = reveal_times(tl, p, at)
        for t in rev:
            if clear(t):
                ev.append({"t": t, "kind": "hit", "db": p["reveal_db"], "lp": 3800.0, "pan": 0.0})
        kh = p.get("key_hits", "all")   # "hook" (v2.2 default): only the opening hit; "all": every key word 4 s apart
        hts = hit_times(tl, p, at) if kh == "all" else ([on_key(tl, tl["captions"][0]["start"] + 0.04)]
                                                         if kh == "hook" and tl["captions"] else [])
        for t in hts:
            if clear(t) and all(abs(t - u) >= SEP for u in rev) and not _in(t, quiet):
                ev.append({"t": t, "kind": "lowhit", "db": p["hit_db"], "lp": 1200.0, "pan": 0.0})
    if p["riser"]:
        from blocky.sound import drop_spec
        drops_ = [at(drop_spec(d)["from"]) for d in snd.get("music_drops", [])]
        tw = at(p["twist"]) if p.get("twist") else None
        # v2.2: a riser is an event, so at most one per riser_gap s, the twist's first, then the drops in order
        ends = []
        for e in ([tw] if tw is not None else []) + sorted(drops_):
            if all(abs(e - u) >= p.get("riser_gap", 15.0) for u in ends):
                ends.append(e)
        for e in sorted(ends):
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


SUSTAIN = ("drone", "pad", "choir")


def music_spec(spec: dict | None) -> dict:
    """v2.2 (owner, 2026-11-03: "there is background music"): the story's own score, made to play from the first
    frame to the last. The first section starts at 0, and a section with no sustained voice gets a quiet drone and
    pad under it, so there's never a stretch of ambience alone. Holes come only from `music_drops`."""
    spec = dict(spec or {})
    secs = [dict(s) for s in spec.get("sections") or [{"at": 0, "voices": ["drone", "pad"], "energy": 0.4}]]
    secs[0]["at"] = 0
    for s in secs:
        v = list(s.get("voices", []))
        if not any(x in v for x in SUSTAIN):
            s["voices"] = v + ["drone", "pad"]
            s["energy"] = min(float(s.get("energy", 0.3)), 0.3) if v else 0.25
    spec["sections"] = secs
    return spec


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


def ones_for_moving(tl: dict, st: dict, p: dict) -> None:
    """`ones: "moving"`: shots on twos where the camera moves (its own keys, a follow, or the pack's move) or
    somebody walks are drawn on every frame, so a move doesn't judder at 15 drawings a second. With the pack's
    camera moves that's nearly every shot: 1.7 to 2.0 times the drawing (docs/research/polish-pack.md → v2.1)."""
    ones_for_walks(tl, st)
    specs = cam_specs(st, tl, p)
    for s in tl["shots"]:
        if s["step"] == 2 and not _static(specs.get(s["id"])):
            s["step"] = 1


def ones_for_walks(tl: dict, st: dict) -> None:
    """`ones: "walk"` (the opt-out from the default "moving"): shots on twos where somebody walks are drawn on every
    frame instead (legs on twos read choppy). It adds about 9% to the drawing on our stories, where "moving" adds 87
    to 98% (docs/research/polish-pack.md)."""
    from blocky import acting
    for s in tl["shots"]:
        if s["step"] != 2:
            continue
        for f in range(s["f0"], s["f1"], 6):
            if any(acting.state(tl, w, f / tl["fps"])["speed"] > 0.05 for w in st.get("cast", {})):
                s["step"] = 1
                break


def auto_cam(shot_spec: dict, p: dict) -> bool:
    """Whether the pack gives this shot a camera move: the camera is on and the shot's own camera holds still."""
    return bool(p and p.get("camera")) and _static(shot_spec) and bool(shot_spec.get("cam"))


CAM_SPEED = 0.12     # m/s: the fastest the pack's push-in goes (critic, ep32 v2: a 0.6 s shot pushed too fast)
CLOSE = 2.0          # m: a camera closer than this to its target pushes in proportionally less (a close-up crops)


def cam_specs(st: dict, tl: dict, p: dict | None) -> dict:
    """Every shot id to its camera spec with the pack's move: what bl_story renders and measure.py reads."""
    lens_ = {s["id"]: s["end"] - s["start"] for s in tl["shots"]}
    calm = set((tl.get("motion") or {}).get("calm_shots", []))
    return {s["id"]: cam_spec(s, i, p, lens_.get(s["id"]), s["id"] in calm) for i, s in enumerate(st["shots"])}


def calm_shots(tl: dict, p: dict, at) -> list[str]:
    """The shots a reveal lands in: they get a straight, slow push and quiet idle motion, so the face that matters
    sits centred and still on the word (critic, ep32 v2: Mum's head and the camera both drifted on "MUM")."""
    rev = reveal_times(tl, p, at)
    return [s["id"] for s in tl["shots"] if any(s["start"] <= t < s["end"] for t in rev)]


def cam_spec(shot_spec: dict, k: int, p: dict | None, dur: float | None = None, calm: bool = False) -> dict:
    """The shot with the pack's slow, motivated camera move when its own camera holds still (craft metrics,
    2026-11-03: the camera moved 27% of the time, back-row's 71%): a push-in of `cam_push` of the distance to the
    target (at most 0.6 m) with a `cam_arc` degree arc round it, the arc turning the other way shot to shot, and every
    third shot a slow sideways truck instead of the arc. bl_story and scripts/measure.py both read the camera
    through this, so the film and the numbers agree."""
    if not p or not auto_cam(shot_spec, p):
        return shot_spec
    k0 = shot_spec["cam"][0]
    loc, tgt, lens = list(k0[1]), list(k0[2]), k0[3]
    rest = list(k0[4:])
    dx, dy, dz = (tgt[i] - loc[i] for i in range(3))
    dist = math.sqrt(dx * dx + dy * dy + dz * dz) or 1.0
    push = min(0.6, dist * p["cam_push"] * min(1.0, dist / CLOSE), CAM_SPEED * dur if dur else 0.6) / dist
    if calm:
        push *= 0.5
    start = [loc[i] + (tgt[i] - loc[i]) * -push / 2 for i in range(3)]
    end = [loc[i] + (tgt[i] - loc[i]) * push / 2 for i in range(3)]
    t0, t1 = list(tgt), list(tgt)
    if calm:
        pass         # a reveal: a straight push only
    elif k % 3 == 1:   # a slow truck sideways (camera and target together)
        side = (-dy, dx)
        n = math.hypot(*side) or 1.0
        sh = 0.035 * dist
        for v, sgn in ((start, -1), (t0, -1), (end, 1), (t1, 1)):
            v[0] += sgn * sh / 2 * side[0] / n
            v[1] += sgn * sh / 2 * side[1] / n
    else:            # an arc round the target, one way then the other
        ang = math.radians(p["cam_arc"]) * (1 if (k // 3) % 2 == 0 else -1) / 2
        for v, sgn in ((start, -1), (end, 1)):
            rx, ry = v[0] - tgt[0], v[1] - tgt[1]
            c, s_ = math.cos(sgn * ang), math.sin(sgn * ang)
            v[0], v[1] = tgt[0] + rx * c - ry * s_, tgt[1] + rx * s_ + ry * c
    if dur:   # the whole move, push plus arc or truck, at most CAM_SPEED (scaled about the camera's own spot)
        travel = math.dist(start, end)
        f = min(1.0, CAM_SPEED * dur / travel) if travel > 1e-9 else 1.0
        start = [loc[i] + (start[i] - loc[i]) * f for i in range(3)]
        end = [loc[i] + (end[i] - loc[i]) * f for i in range(3)]
        t0 = [tgt[i] + (t0[i] - tgt[i]) * f for i in range(3)]
        t1 = [tgt[i] + (t1[i] - tgt[i]) * f for i in range(3)]
    return {**shot_spec, "cam": [[0, start, t0, lens, *rest], [1, end, t1, lens, *rest]], "auto_cam": True}


_QUIET: dict = {}


def _quiet_cache(tl: dict, p: dict) -> list:
    key = (id(tl), id(p))
    if key not in _QUIET:
        from blocky.timeline import resolver
        _QUIET.clear()
        _QUIET[key] = quiet_spans(p, resolver(tl["lines"], tl["duration"])) if p.get("quiet") else []
    return _QUIET[key]


def reframe_times(tl: dict, p: dict) -> list[float]:
    """When the pack's angle cuts land: in shots over `reframe_min` s that aren't a reveal shot and don't touch a
    quiet span, about every `reframe_every` s, each moved to the nearest caption change within 0.35 s (cut with the
    words) and dropped when there's none, or when it would leave a part under 0.6 s."""
    out = []
    rf = p.get("reframe_every")
    if not rf:
        return out
    calm = set((tl.get("motion") or {}).get("calm_shots") or [])
    quiet = _quiet_cache(tl, p)
    caps = [c["start"] for c in tl["captions"]]
    for s in tl["shots"]:
        L = s["end"] - s["start"]
        if L < p.get("reframe_min", 1.6) or s["id"] in calm:
            continue
        if any(a < s["end"] and b > s["start"] for a, b in quiet):
            continue
        nseg = max(2, int(round(L / rf)))
        last = s["start"]
        for i in range(1, nseg):
            want = s["start"] + i * L / nseg
            near = [c for c in caps if abs(c - want) <= 0.35 and c - last >= 0.6 and s["end"] - c >= 0.6]
            if near:
                last = min(near, key=lambda c: abs(c - want))
                out.append(last)
    return out


_REFRAME: dict = {}


def _reframe_cache(tl: dict, p: dict) -> list:
    key = (id(tl), id(p))
    if key not in _REFRAME:
        _REFRAME.clear()
        _REFRAME[key] = reframe_times(tl, p)
    return _REFRAME[key]


def motion(tl: dict, st: dict, p: dict, t: float, emph: list[float] | None = None) -> tuple[float, float, float]:
    """The pack's camera move at time t, on the output crop: (zoom, dx, dy), dx and dy as fractions of the frame."""
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    k = tl["shots"].index(shot)
    sspec = next((s for s in st.get("shots", []) if s["id"] == shot["id"]), None)
    length = shot["end"] - shot["start"]
    u = (t - shot["start"]) / max(1e-6, length)
    zoom, dx, dy = 1.0, 0.0, 0.0
    if p["drift"] and length >= p["drift_min"] and _static(sspec) and not auto_cam(sspec or {}, p):
        # alternate in and out shot to shot, with a slow sideways slide, eased at both ends of the shot
        e = _ease(u) * 0.7 + u * 0.3
        d = p["drift"]
        zoom = 1 + d * (e if k % 2 == 0 else 1 - e) + d * 0.2
        side = 1 if (k // 2) % 2 == 0 else -1
        dx = side * d * 0.15 * (e - 0.5)
    calm = shot["id"] in ((tl.get("motion") or {}).get("calm_shots") or [])
    if p.get("push"):
        # pace (v2.3, craft metrics blocks 2026-11-03): a steady crop push through every shot, in on one shot and
        # out on the next, at a constant rate so every 0.25 s reads as a change (an eased move stalls at its ends)
        pu = p["push"] * (0.5 if calm else 1.0)
        zoom *= 1 + pu * (u if k % 2 == 0 else 1 - u)
        dx += (1 if (k // 2) % 2 == 0 else -1) * pu * 0.12 * (u - 0.5)
    rf = p.get("reframe_every")
    if rf:
        # an angle cut inside a long shot (v2.3): every other part is a tighter framing, centred and a touch up
        # (an offset pushed faces off the edge, critic ep32), cut on a caption change (never under a held word)
        cuts_ = [c for c in _reframe_cache(tl, p) if shot["start"] < c < shot["end"]]
        seg = sum(1 for c in cuts_ if c <= t)
        if seg % 2 == 1:
            zoom *= p.get("reframe_zoom", 1.12)
            dy -= 0.015
    if p["punch"]:
        for te in emph if emph is not None else emph_times(tl, p):
            if shot["start"] - 1e-6 <= te < shot["end"] and t >= te:
                # held to the cut (no zoom back out mid-shot), at most 2.5 s, then it eases back over 0.4 s
                x = t - te
                amt = _ease(x / 0.12) * (1 - _ease((x - 2.5) / 0.4))
                zoom *= 1 + min(p["punch"], (p.get("punch_cap") or {}).get(shot["id"], p["punch"])) * amt
    sway = p.get("sway")
    if sway and (sway is True or shot["id"] in sway):
        a = p["sway_amp"]
        dx += a * (math.sin(t * 2 * math.pi * 0.31 + 1.3) + 0.5 * math.sin(t * 2 * math.pi * 0.53))
        dy += a * 0.7 * (math.sin(t * 2 * math.pi * 0.23 + 0.4) + 0.4 * math.sin(t * 2 * math.pi * 0.47 + 2.0))
    zoom = min(zoom, p.get("max_zoom", 1.25))   # the drawings are 540 wide: past 1.25 the crop goes soft
    return zoom, dx, dy                        # (post.to_output widens the crop to fit any slide)


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
    if pr.get("red_line"):   # v2.3: the pack's push and angle cuts enlarge red areas, so keep under WCAG's saturated
        # red on every frame (ep32 S09b: 47.7% of the screen without pace, 53% with it, against the 50% red-frame bar)
        out["red_line"] = min(g.get("red_line", 1.0), pr["red_line"])
    return out


def caption_scale(x: float) -> float:
    """The polish caption pop: 90% to 100% over 80 ms, eased out (x = seconds since the caption appeared)."""
    if x >= 0.08:
        return 1.0
    u = max(0.0, x) / 0.08
    return 0.9 + 0.1 * (1 - (1 - u) ** 3)
