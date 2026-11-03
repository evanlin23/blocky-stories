"""The edit for one blocky story, from its spec (`stories/<name>/story.json`) and the narrator's real word timings
(`stories/<name>/voice-timings.json`, written by `voice`). Pure Python: the tests, the sound, the post and
Blender all read the timeline this writes.

- Lines play one after another with each line's `gap` (default 0.12 s: the reference barely breathes).
- Captions follow the voice two or three words at a time: each chunk shows from its first word until the next
  chunk starts. A caption never waits for the one before it, so it can't drift behind the voice.
- Shots cut at time references (below), so a cut lands on the word it belongs to.
- A character who says a line gets one mouth flap per syllable. The narrator is a voice-over: no mouth moves.

A time reference is a number of seconds, or a line id with an optional chunk and offset:
    "L03"      the line's first word         "L03.2"   chunk 2's first word (0-based)
    "L03>"     the line's last word ends     "L03.2>"  chunk 2's last word ends
    "L03+0.4"  0.4 s after L03 starts        "end-1.5" 1.5 s before the film ends
    "P02"      a pause beat's start (its id)  "P02>"    the pause beat's end
"""

from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
STORIES = HERE.parent / "stories"
FPS = 30
LEAD = 0.25          # before the first word
TAIL = 0.9           # after the last word
GAP = 0.12           # between lines unless the line says otherwise
CAPTION_LEAD = 0.04  # a chunk shows a hair before its first word
MIN_CAPTION = 0.42   # the last chunk, and a chunk before a long pause, stay up at least this long
MIN_HOLD = 0.35      # how long a chunk holds past its last word before a pause
MIN_READ = 0.22      # a chunk up for less than this joins the next one in its line (a story can raise it: "min_read")
MERGE_WORDS = 4      # ...as long as the joined caption is at most this many words
REF = re.compile(r"^(?P<base>[LP]\w+?|end|start)(?:\.(?P<chunk>\d+))?(?P<tail>>)?(?P<off>[+-]\d+(?:\.\d+)?)?$")


def story_dir(name: str) -> Path:
    d = STORIES / name
    if not (d / "story.json").exists():
        raise SystemExit(f"no story {name!r}: expected {d / 'story.json'}")
    return d


def load_story(name: str) -> dict:
    st = json.loads((story_dir(name) / "story.json").read_text())
    st.setdefault("name", name)
    return st


def syllables(text: str) -> int:
    n = 0
    for w in re.findall(r"[a-z]+", text.lower()):
        g = len(re.findall(r"[aeiouy]+", w))
        if w.endswith("e") and not w.endswith(("le", "ee")) and g > 1:
            g -= 1
        n += max(1, g)
    n += len(re.findall(r"\d+", text))
    return max(1, n)


def resolver(placed: dict, duration: float | None):
    def at(ref) -> float:
        if isinstance(ref, (int, float)):
            return float(ref)
        s = str(ref).strip()
        try:
            return float(s)
        except ValueError:
            pass
        m = REF.match(s)
        if not m:
            raise SystemExit(f"bad time reference {ref!r}")
        base, off = m.group("base"), float(m.group("off") or 0)
        if base == "start":
            return off
        if base == "end":
            if duration is None:
                raise SystemExit("'end' isn't known yet")
            return duration + off
        if base not in placed:
            raise SystemExit(f"time reference {ref!r}: no line {base}")
        p = placed[base]
        if m.group("chunk") is not None:
            k = int(m.group("chunk"))
            if k >= len(p["chunks"]):
                raise SystemExit(f"time reference {ref!r}: {base} has {len(p['chunks'])} chunks")
            a, b = p["chunks"][k][:2]
        else:
            a, b = p["onset"], p["end"]
        return round((b if m.group("tail") else a) + off, 3)
    return at


def captions(placed: dict, order: list, duration: float, min_read: float = MIN_READ) -> list[dict]:
    """Each chunk shows on its own first word, always: a caption never waits for the one before it (owner,
    2026-10-30: "it looks like the captions are slightly out of sync with the voice"). It stays up until the
    next chunk starts, so at the sped-up pace a short chunk is on screen for as long as it's being said. Over a
    long pause it holds MIN_HOLD past its last word rather than sitting through the silence."""
    flat = [(placed[l], c) for l in order for c in placed[l]["chunks"]]
    caps = []
    for i, (p, (a, b, text)) in enumerate(flat):
        s = max(0.0, a - CAPTION_LEAD)
        nxt = flat[i + 1][1][0] - CAPTION_LEAD if i + 1 < len(flat) else duration
        e = nxt - 0.01
        if nxt - b > 0.6:  # a long pause: don't hold the words over it
            e = min(e, max(b + MIN_HOLD, s + MIN_CAPTION))
        e = min(e, duration)
        caps.append({"line": p["id"], "who": p["who"], "text": text, "start": round(s, 3), "end": round(e, 3),
                     "big": p["who"] == "pause"})
    # a chunk said too fast to read ("On the", "in a") joins the next chunk of the same line, up to MERGE_WORDS:
    # "On the BACK ROW" shows from "On", instead of a two-word flash
    return _joined(caps, min_read)


def _fits(text: str) -> bool:
    from blocky import post   # PIL; only the repo's Python builds timelines
    return not [p for p in post.layout_problems([{"text": text}]) if "words" not in p]


def _joined(caps: list[dict], min_read: float = MIN_READ) -> list[dict]:
    """Join each too-short caption onto the next caption of its line while the words fit the safe area."""
    out = []
    i = 0
    while i < len(caps):
        c = dict(caps[i])
        while (i + 1 < len(caps) and c["end"] - c["start"] < min_read and not c["big"]
               and caps[i + 1]["line"] == c["line"] and not caps[i + 1]["big"]
               and len(c["text"].split()) + len(caps[i + 1]["text"].split()) <= MERGE_WORDS
               and _fits(c["text"] + " " + caps[i + 1]["text"])):
            n = caps[i + 1]
            c = {**c, "text": c["text"] + " " + n["text"], "end": n["end"]}
            i += 1
        out.append(c)
        i += 1
    return out


def build(st: dict, voice: dict, fps: int = FPS) -> dict:
    vl = voice["lines"]
    t = LEAD
    placed = {}
    order = []
    for ln in st["lines"]:
        lid = ln["id"]
        if "pause" in ln:  # a beat with no words (a sound, a held shot)
            # its big words pop one chunk at a time: at its "times" (seconds into the beat), or spread evenly
            cs = [c for c, _ in ln.get("chunks", [])]
            ts = ln.get("times") or [ln["pause"] * i / max(1, len(cs)) for i in range(len(cs))]
            ends = list(ts[1:]) + [ln["pause"]]
            placed[lid] = {"id": lid, "who": "pause", "onset": round(t, 3), "end": round(t + ln["pause"], 3),
                           "chunks": [[round(t + a, 3), round(t + b, 3), c] for a, b, c in zip(ts, ends, cs)]}
            order.append(lid)
            t += ln["pause"]
            continue
        if lid not in vl:
            raise SystemExit(f"{lid} has no voice timing: run `python -m blocky voice {st['name']}`")
        v = vl[lid]
        shift = t - v["onset"]
        chunks = [[round(a + shift, 3), round(b + shift, 3), cap] for (a, b), (cap, _) in zip(v["chunks"], ln["chunks"])]
        placed[lid] = {"id": lid, "who": ln.get("who", "narrator"), "text": v["text"], "wav": v.get("wav", f"{lid}.wav"),
                       "wav_at": round(shift, 3), "onset": round(t, 3), "end": round(v["end"] + shift, 3),
                       "chunks": chunks}
        if ln.get("space"):
            placed[lid]["space"] = ln["space"]   # some of its chunks heard from further off (sound.narration)
        if ln.get("gain_db"):
            placed[lid]["gain_db"] = float(ln["gain_db"])   # a quieter (or louder) line in the narration mix
        order.append(lid)
        t = v["end"] + shift + ln.get("gap", st.get("gap", GAP))
    last = placed[order[-1]]
    frame_up = lambda x: round(-(-x * fps // 1) / fps, 4)
    duration = frame_up(last["end"] + st.get("tail", TAIL))
    caps = captions(placed, order, duration, float(st.get("min_read", MIN_READ)))
    if caps and caps[-1]["end"] - caps[-1]["start"] < MIN_CAPTION - 1e-6:
        # a short tail (a loop has none): hold the last picture just long enough for the last caption to read
        duration = frame_up(caps[-1]["start"] + MIN_CAPTION)
        caps = captions(placed, order, duration, float(st.get("min_read", MIN_READ)))
    at = resolver(placed, duration)

    # mouths: one flap per syllable over each chunk, for lines a character says on screen
    cast = st.get("cast", {})
    talk = {name: [] for name in cast}
    for l in order:
        p = placed[l]
        if p["who"] not in talk:
            continue
        spoken = next(ln for ln in st["lines"] if ln["id"] == l)["chunks"]
        for (a, b, _), (_, sp) in zip(p["chunks"], spoken):
            n = syllables(sp)
            step = (b - a) / n
            for k in range(n):
                talk[p["who"]].append([round(a + k * step, 3), round(min(step * 0.85, 0.2), 3)])

    shots = []
    specs = st["shots"]
    starts = [0.0] + [at(s["at"]) for s in specs[1:]]
    for i, s in enumerate(specs):
        a = starts[i]
        b = starts[i + 1] if i + 1 < len(specs) else duration
        if b <= a:
            raise SystemExit(f"shot {s['id']} has no length ({a:.2f} to {b:.2f})")
        f0, f1 = int(round(a * fps)), int(round(b * fps))
        # exact frame times, not rounded: a frame's t = f / fps must compare equal to its own shot's start, or the
        # first frame of a cut is drawn with the previous shot's camera (standards found it at 32 of ep11's 81 cuts)
        shots.append({"id": s["id"], "start": f0 / fps, "end": f1 / fps, "f0": f0, "f1": f1,
                      "step": s.get("step", 2)})
    # a cue, effect or acting key anchored to the same word as a cut lands a few ms after the shot's first frame
    # (the cut is rounded to a frame, the word isn't), so that frame showed the previous shot's state (standards,
    # ep12 R7: night before dawn, Ray where I should be). Snap anything inside a shot's first frame to the cut.
    starts = [s["start"] for s in shots]

    def snap(t: float) -> float:
        for a in starts:
            if a < t < a + 1.0 / fps - 1e-9:
                return a
        return t

    cues = [{**c, "t": snap(at(c["at"]))} for c in st.get("cues", [])]
    fx = [{**f, "t": snap(at(f["at"]))} for f in st.get("fx", [])]
    acting = {who: [{**k2, "t": snap(k2["t"])} for k2 in (_key(k, at) for k in keys)]
              for who, keys in st.get("acting", {}).items()}
    return {"name": st["name"], "fps": fps, "duration": duration, "frames": int(round(duration * fps)),
            "tail": st.get("tail", TAIL),
            "fade_out": st.get("fade_out", True),
            "fade_in": st.get("fade_in", True),
            "voice": {k: voice.get(k) for k in ("voice", "rate", "tempo", "model")},
            "lines": placed, "order": order, "captions": caps, "talk": talk, "shots": shots,
            "cues": cues, "fx": fx, "acting": acting, "motion": _motion(st)}


def _motion(st: dict) -> dict:
    """The polish pack's acting options for acting.py (eased walks, idle life); {} without the pack."""
    from blocky import polish
    p = polish.spec(st)
    if not p:
        return {}
    return {"ease": bool(p["ease"]), "idle": bool(p["idle"]), "idle_scale": float(p["idle_scale"])}


def _key(k: dict, at) -> dict:
    """An acting key with its times resolved: "at" -> t, and a mouth key's "from"/"to" -> t0/t1 (t = t0, so
    the key sorts where it starts and holds nothing else)."""
    if "from" in k:
        t0, t1 = at(k["from"]), at(k["to"])
        if t1 <= t0:
            raise SystemExit(f"mouth key {k['from']!r} to {k['to']!r} has no length")
        return {**k, "t": t0, "t0": t0, "t1": t1}
    return {**k, "t": at(k.get("at", 0))}


def write(name: str, voice_json: Path, out: Path) -> dict:
    tl = build(load_story(name), json.loads(Path(voice_json).read_text()))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(tl, indent=1, ensure_ascii=False))
    return tl


def cue(tl: dict, name: str, default: float | None = None) -> float | None:
    for c in tl["cues"]:
        if c["name"] == name:
            return c["t"]
    return default


def shot_at(tl: dict, t: float) -> dict:
    for s in tl["shots"]:
        if s["start"] <= t < s["end"]:
            return s
    return tl["shots"][-1]


def frame_list(tl: dict, step_override: int | None = None) -> list[int]:
    out = []
    for s in tl["shots"]:
        step = step_override or s["step"]
        out += list(range(s["f0"], s["f1"], step))
    return out
