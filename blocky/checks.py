"""Checks for a blocky story, run by `python -m blocky check <story>` and the tests (note 18).

Fiction passes: a blocky story needs no fact and no source. What blocks:
- a claim that it's real ("true story", "this really happened", "based on real events" ...)
- graphic or mature content: gore, killing and death described, sexual content, self-harm, real crimes
- harm to a child shown or described: a cast member under 13 is refused outright, and no line may put a
  kid, child, baby, little boy or little girl next to a harm word
- the game's name anywhere a viewer reads or hears it, the title included
- `made_for_kids` must be false, and every cast member needs an `age` ("teen" or "adult")
- the default-face look (faces.check_original)
- house rule 9 (voicecheck.py) on every caption, spoken line and the title
- the caption layout (two or three words, cap height, safe area) and the timeline (30 to 60 s, caption times)
- originality against every other story in `stories/`: its own set file, cast, words and twist (YouTube's
  first example of mass-produced content is "narrated stories with only superficial differences")
Warnings: the pace if it's far from the reference's 280 to 300 wpm.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from blocky import faces
from blocky.timeline import STORIES, load_story

TRUE_CLAIM = re.compile(r"\b(true story|truly happened|really happened|actually happened|this happened to me|"
                        r"based on (a )?(true|real)|real events|real story|not (fake|made up)|100% real|"
                        r"i swear (it'?s|this is) real|caught on camera|real footage|documented case)\b", re.I)
GRAPHIC = re.compile(r"\b(blood\w*|bleed\w*|gore|gory|guts|corpse\w*|dead bod(y|ies)|stab\w*|decapitat\w*|"
                     r"dismember\w*|behead\w*|mutilat\w*|entrails|severed|murder\w*|kill\w*|slaughter\w*|"
                     r"massacre\w*|tortur\w*|suicid\w*|self[- ]?harm|cut (my|him|her|them)sel\w*|hang(ed)? (him|her|my|them)sel\w*|"
                     r"overdos\w*|sex\w*|nude|naked|rape\w*|molest\w*|kidnap\w*|abduct\w*|serial killer|shooting|gun\w*|"
                     r"knife|knives|dead|die[sd]?|dying|death)\b", re.I)
CHILD = re.compile(r"\b(kids?|child(ren)?|bab(y|ies)|toddler\w*|little (boy|girl|brother|sister)|son|daughter)\b", re.I)
HARM = re.compile(r"\b(hurt\w*|grab\w*|took|taken|drag\w*|vanish\w*|disappear\w*|missing|attack\w*|bit(e|ten)|"
                  r"fell|fall\w*|drown\w*|lost|scream\w*|cry\w*|pulled|eaten|ate|swallow\w*|chas\w*|trapped|locked)\b", re.I)
BRAND = re.compile(r"r\W*o\W*b\W*l\W*o\W*x", re.I)
AGES = ("teen", "adult")
MIN_S, MAX_S = 15.0, 180.0  # 15 s allows the ultra-short tests (the trend scan's fastest POV clips run 13 to 44 s); 3 min is the Shorts limit


def texts(st: dict) -> tuple[list[str], list[str]]:
    screen = [c for ln in st["lines"] for c, _ in ln.get("chunks", [])]
    said = [" ".join(s for _, s in ln.get("chunks", []) if s) for ln in st["lines"]]
    return screen, said


def _trigrams(words):
    w = [re.sub(r"[^a-z']", "", x.lower()) for x in words]
    w = [x for x in w if x]
    return {tuple(w[i:i + 3]) for i in range(len(w) - 2)}


def originality(name: str, st: dict) -> list[tuple[str, str]]:
    out = []
    mine = STORIES / name
    my_set = hashlib.sha256((mine / "set.py").read_bytes()).hexdigest() if (mine / "set.py").exists() else None
    my_words = " ".join(texts(st)[1]).split()
    my_tri = _trigrams(my_words)
    my_cast = {json.dumps(v, sort_keys=True) for v in st.get("cast", {}).values()}
    for other in sorted(p for p in STORIES.iterdir() if (p / "story.json").exists() and p.name != name
                        and not p.name.startswith("_")):
        o = json.loads((other / "story.json").read_text())
        if my_set and (other / "set.py").exists() and hashlib.sha256((other / "set.py").read_bytes()).hexdigest() == my_set:
            out.append(("block", f"set.py is a copy of {other.name}'s: every story builds its own world"))
        tri = _trigrams(" ".join(texts(o)[1]).split())
        if my_tri:
            share = len(my_tri & tri) / len(my_tri)
            if share > 0.12:
                out.append(("block", f"{share:.0%} of its three-word phrases are in {other.name}: a template with the words swapped"))
        same = my_cast & {json.dumps(v, sort_keys=True) for v in o.get("cast", {}).values()}
        if same:
            out.append(("block", f"{len(same)} cast member(s) are identical to {other.name}'s"))
        for k in ("premise", "twist", "world"):
            mine_k, theirs_k = st.get(k), o.get(k)
            if isinstance(mine_k, str) and isinstance(theirs_k, str) and mine_k.strip() \
                    and mine_k.strip().lower() == theirs_k.strip().lower():
                out.append(("block", f"same {k} as {other.name}"))
    return out


CUT_MAX_S = 2.3


# effects that are mostly bright noise (over a quarter of their energy above 4 kHz, measured 2026-11-02): fine as a
# rare, quiet accent, scratchy when loud or repeated (the owner pulled ep36 over its hissy grass steps)
HARSH_SFX = {"glitch", "tape", "rasp", "radio"}   # click is a tiny transient tick, not a hiss: back-row held 84% with 15


def harsh_sound(st: dict) -> list[tuple[str, str]]:
    sfx = [s for s in (st.get("sound") or {}).get("sfx", []) if s.get("kind") in HARSH_SFX]
    loud = [f"{s['kind']}@{s.get('at')}" for s in sfx if float(s.get("db", -30)) > -24]
    out = []
    if loud:
        out.append(("warn", f"bright, noisy effects above -24 dB can sound scratchy: {loud[:5]} (keep them quiet)"))
    for a in (st.get("sound") or {}).get("ambience", []):
        if a.get("kind") == "static" and float(a.get("lufs", -40)) > -40:   # radio hiss: 90% of it above 4 kHz
            out.append(("warn", f"static ambience at {a.get('lufs')} LUFS will sound like hiss; keep it under -40"))
    if len(sfx) > 6:
        out.append(("warn", f"{len(sfx)} bright, noisy effects; repeated, they read as scratching (ep36's grass steps)"))
    return out


NARRATOR_MISFIT = re.compile(r"\bmy (husband|boyfriend|hubby)\b", re.I)   # the one narrator voice is a man's (ep38)


def run(name: str, timeline: Path | None = None, st: dict | None = None) -> list[tuple[str, str]]:
    from blocky import voicecheck as sc

    from blocky import post

    st = st if st is not None else load_story(name)
    out = []
    set_py = STORIES / name / "set.py"   # tests pass in-memory stories with no folder
    if set_py.exists() and "flicker" in set_py.read_text() and not (st.get("look") or {}).get("flash_safe"):
        out.append(("warn", "the set has flickering lights but look.flash_safe isn't set; strobing flicker failed the "
                            "flash bar on most stories (RULES.md hard rule 7)"))
    out += harsh_sound(st)
    said_all = " ".join(" ".join(c[1] for c in ln.get("chunks", [])) for ln in st.get("lines", []))
    if NARRATOR_MISFIT.search(said_all):
        out.append(("warn", "the narrator says 'my husband/boyfriend', but the narrator voice is a man's (ep38): "
                             "make the narrator's family fit a man"))
    screen, said = texts(st)
    viewer = screen + said + [st.get("title", "")]
    for i, ln in enumerate(st["lines"]):
        for text in [c for c, _ in ln.get("chunks", [])] + [said[i]]:
            if TRUE_CLAIM.search(text):
                out.append(("block", f"{ln['id']}: claims it's real: {text!r} (blocky stories are fiction, note 18)"))
            m = GRAPHIC.search(text)
            if m:
                out.append(("block", f"{ln['id']}: {m.group(0)!r} is graphic or mature: {text!r} (suspense and the uncanny only)"))
        line_text = said[i]
        if CHILD.search(line_text) and HARM.search(line_text):
            out.append(("block", f"{ln['id']}: a child next to harm: {line_text!r} (no harm to a child shown or described)"))
    for t in viewer + [st.get("premise", ""), st.get("twist", "")]:
        if BRAND.search(t):
            out.append(("block", f"the game's name appears: {t!r} (titles, captions and lines never say it)"))
        if TRUE_CLAIM.search(t):
            out.append(("block", f"claims it's real: {t!r}"))
    if st.get("made_for_kids", True) is not False:
        out.append(("block", "made_for_kids must be false: kid-styled art with mature themes is removed (note 18)"))
    for who, spec in st.get("cast", {}).items():
        if spec.get("age") not in AGES:
            out.append(("block", f"cast {who}: age must be one of {AGES} (no child characters in peril)"))
        for p in faces.check_original(spec.get("face", {})):
            out.append(("block", f"cast {who}: {p}"))
    whos = set(st.get("cast", {})) | {"narrator", "pause"}
    for ln in st["lines"]:
        if ln.get("who", "narrator") not in whos:
            out.append(("block", f"{ln['id']}: who {ln.get('who')!r} isn't in the cast"))
    for r in sc.voice_results(screen, said + [st.get("title", "")]):
        if r.level != "pass":
            out.append((r.level, f"note 9: {r.message}"))
    caps = [{"text": c, "big": "pause" in ln} for ln in st["lines"] for c, _ in ln.get("chunks", [])]
    out += [("block", p) for p in post.layout_problems(caps)]
    out += originality(name, st)
    if timeline and Path(timeline).exists():
        tl = json.loads(Path(timeline).read_text())
        if not MIN_S <= tl["duration"] <= MAX_S:
            out.append(("block", f"{tl['duration']:.1f} s, outside {MIN_S:g} to {MAX_S:g} s"))
        for c in tl["captions"]:
            if c["end"] - c["start"] < 0.1 - 1e-6:
                out.append(("block", f"caption {c['text']!r} is up {c['end'] - c['start']:.2f} s (< 0.1): merge it"))
        flick = [c["text"] for c in tl["captions"] if c["end"] - c["start"] < 0.2 - 1e-6]
        if flick:
            out.append(("warn", f"{len(flick)} caption(s) up under 0.2 s (they follow the voice): {flick[:4]}"))
        late = [c["text"] for c in tl["captions"] if not any(abs(c["start"] - (a - 0.04)) < 1e-3
                for a, _b, _t in tl["lines"][c["line"]]["chunks"])] if tl["captions"] and "lines" in tl else []
        if late:
            out.append(("block", f"{len(late)} caption(s) don't start on a chunk's first word: {late[:4]}"))
        words = sum(len(tl["lines"][l].get("text", "").split()) for l in tl["order"])
        span = max(1e-6, tl["lines"][tl["order"][-1]]["end"] - tl["lines"][tl["order"][0]]["onset"])
        wpm = words / span * 60
        if not 230 <= wpm <= 330:
            out.append(("warn", f"{wpm:.0f} wpm overall; the reference runs 280 to 300"))
        shot_ids = [s["id"] for s in st["shots"]]
        if len(set(shot_ids)) != len(shot_ids):
            out.append(("block", "two shots share an id"))
        if tl.get("shots"):   # the hits cut every 1.2 to 2.3 s on average (RULES.md, What the hits do 9)
            per = tl["duration"] / len(tl["shots"])
            if per > CUT_MAX_S:
                out.append(("warn", f"a shot every {per:.1f} s on average; the hits cut every 1.2 to 2.3 s "
                                    f"(about {int(tl['duration'] / CUT_MAX_S) + 1} shots for this length)"))
    return out
