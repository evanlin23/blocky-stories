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
STILL_MAX_S = 1.0    # measure.py's block: no picture still for more than 1.0 s (the browser study of 17 hits)
CUTS_MIN_PER_10S = 5.5


def _cam_at(spec: dict, shot: dict, t: float, tl: dict):
    """The camera's (loc, target, lens) at t from its keys, as bl_story places it (no handheld drift)."""
    from blocky import acting

    keys = spec["cam"]
    u = (t - shot["start"]) / max(1e-6, shot["end"] - shot["start"])
    ease = lambda v: (lambda x: x * x * (3 - 2 * x))(min(1.0, max(0.0, v)))
    k = keys[-1]
    loc, tgt, lens = k[1], k[2], k[3]
    if u <= keys[0][0] or len(keys) == 1:
        loc, tgt, lens = keys[0][1], keys[0][2], keys[0][3]
    else:
        for a, b in zip(keys, keys[1:]):
            if u <= b[0]:
                v = ease((u - a[0]) / max(1e-6, b[0] - a[0]))
                loc = [x + (y - x) * v for x, y in zip(a[1], b[1])]
                tgt = [x + (y - x) * v for x, y in zip(a[2], b[2])]
                lens = a[3] + (b[3] - a[3]) * v
                break
    if spec.get("follow") and spec["follow"] in tl.get("acting", {}):
        s = acting.state(tl, spec["follow"], t)
        loc = [loc[0] + s["x"], loc[1] + s["y"], loc[2] + s["z"]]
        tgt = [tgt[0] + s["x"], tgt[1] + s["y"], tgt[2] + s["z"]]
    return list(loc), list(tgt), float(lens)


def still_spans(st: dict, tl: dict, dt: float = 0.1) -> list[tuple[str, float, float]]:
    """Stretches inside one shot where, by the edit alone, nothing moves: the camera (its keys, follow and the
    polish pack's moves), the crop (punch-ins, drift, sway) and every character's pose all hold. (shot id, start,
    end) for each one over STILL_MAX_S. Something set.py's animate() moves can't be seen here: list such shots
    in story.json's `"set_moves": [shot ids]`. A lower bound on what the final shows, so a hit here always fails."""
    from blocky import acting, polish, post

    if not tl.get("shots"):
        return []
    pol = polish.spec(st)
    specs = polish.cam_specs(st, tl, pol)
    emph = polish.emph_times(tl, pol) if pol else []
    skip = set(st.get("set_moves", []))
    cast = [k for k, v in st.get("cast", {}).items() if not v.get("offscreen")]

    def frame(t):
        z = post.fx_at(tl, t)["punch"]
        zz, dx, dy = polish.motion(tl, st, pol, t, emph) if pol else (1.0, 0.0, 0.0)
        poses = []
        for w in cast:
            s = acting.state(tl, w, t)
            poses.append(None if s["hidden"] else [s["x"], s["y"], s["z"], s["yaw"], s["legs"], *s["arms"],
                                                    *s["arms_side"], s["head_yaw"], s["head_pitch"], s["lean"],
                                                    s["bob"], s["mouth"]])
        return z * zz, dx, dy, poses

    out = []
    for sh in tl["shots"]:
        if sh["id"] in skip or sh["id"] not in specs or "cam" not in specs[sh["id"]]:
            continue
        n = int((sh["end"] - sh["start"]) / dt)
        prev, run0 = None, None
        for i in range(n + 1):
            t = min(sh["start"] + i * dt, sh["end"] - 1e-3)
            cam = _cam_at(specs[sh["id"]], sh, t, tl)
            fr = frame(t)
            moved = True
            if prev is not None:
                pc, pf = prev
                moved = (max(abs(a - b) for a, b in zip(cam[0] + cam[1], pc[0] + pc[1])) > 0.003
                         or abs(cam[2] - pc[2]) > 0.03 or abs(fr[0] - pf[0]) > 0.002
                         or abs(fr[1] - pf[1]) > 0.002 or abs(fr[2] - pf[2]) > 0.002
                         or any((a is None) != (b is None) or (a is not None and max(abs(x - y) for x, y in zip(a, b)) > 0.01)
                                for a, b in zip(fr[3], pf[3])))
            if moved:
                if run0 is not None and t - dt - run0 > STILL_MAX_S + 1e-6:
                    out.append((sh["id"], round(run0, 2), round(t - dt, 2)))
                run0 = t
            prev = (cam, fr)
        end = min(sh["start"] + n * dt, sh["end"])
        if run0 is not None and end - run0 > STILL_MAX_S + 1e-6:
            out.append((sh["id"], round(run0, 2), round(end, 2)))
    return out


def still_risks(st: dict, tl: dict) -> list[str]:
    """still_spans as messages: what the proof and the final would fail on (measure.py longest_still_q_s)."""
    return [f"{sid} {a:.1f}-{b:.1f} s: nothing moves for {b - a:.1f} s (camera, crop and cast all hold); the film's "
            f"longest still must be at most {STILL_MAX_S:g} s. Key a move, a pose or a punch-in there (or list the "
            f"shot in story.json `set_moves` if set.py animates something big in it)" for sid, a, b in still_spans(st, tl)]


def clip_times(tl: dict, st: dict | None = None, every: float = 0.25) -> list[float]:
    """When `clipcheck` poses the film: every `every` seconds plus every acting key (where a pose lands), each on
    a frame, in order."""
    fps, dur = tl["fps"], tl["duration"]
    ts = [i * every for i in range(int(dur / every) + 1)]
    ts += [k["t"] for keys in tl.get("acting", {}).values() for k in keys if "t" in k]
    frames = sorted({min(tl["frames"] - 1, max(0, int(round(t * fps)))) for t in ts if 0 <= t < dur})
    return [round(f / fps, 4) for f in frames]


CAM_NEAR = 0.25   # metres: a surface this close to the lens, over CAM_FILL of the frame, is a wall in front of it
CAM_FILL = 0.7    # share of the frame (a 7 x 7 grid of rays through it)
CAM_GRID = 7
CAM_FLAT = 0.95   # one flat surface (not a character) over this share of the frame, within CAM_FLAT_FAR: a blank
CAM_FLAT_FAR = 3.0


def cam_times(tl: dict, st: dict) -> list[tuple[float, str]]:
    """When `clipcheck` tests where the camera is: each shot's first and last frame and every key of its camera
    move (ep120 S67's pull-in ended behind a window: 9 blank cream frames). On frames, in order."""
    fps = tl["fps"]
    specs = {s["id"]: s for s in st.get("shots", [])}
    out = set()
    for sh in tl["shots"]:
        f0, f1 = sh["f0"], max(sh["f0"], sh["f1"] - 1)
        fs = {f0, f1}
        for k in specs.get(sh["id"], {}).get("cam", []):
            fs.add(min(f1, max(f0, int(round((sh["start"] + k[0] * (sh["end"] - sh["start"])) * fps)))))
        out |= {(f / fps, sh["id"]) for f in fs}   # exact: a rounded t can fall before its own shot's start
    return sorted(out)


def cam_verdict(axis: list, grid: list, near: float = CAM_NEAR, fill: float = CAM_FILL, cast=()) -> dict | None:
    """Is the camera inside something, or right behind a surface that fills the frame?
    `axis`: for six rays from the lens along +-x, +-y, +-z, (object name or None, the hit face looks away from
    the lens). `grid`: for rays through the frame, (distance or None, object name, ...). Inside: five of the six
    axis rays hit the back of one object (a house with no floor is open below: ep105 S139). Seeing the back of
    something across the frame isn't enough on its own: that's also a shot through a window pane. A wall: `fill` or more of the frame stops within `near` metres (a
    face fills the frame from 0.3 m and further, so a close-up passes). Flat: one surface that isn't one of the
    `cast` covers CAM_FLAT of the frame within CAM_FLAT_FAR, all at about one distance.
    Returns {"kind": "inside"|"wall", "what": name, "share": s} or None."""
    backs = [a for a, b in axis if a is not None and b]
    if backs:
        top = max(set(backs), key=backs.count)
        if backs.count(top) >= 5:
            return {"kind": "inside", "what": top, "share": round(backs.count(top) / 6, 2)}
    close = [g[1] for g in grid if g[0] is not None and g[0] < near]
    if grid and len(close) >= fill * len(grid):
        what = max(set(close), key=close.count)
        return {"kind": "wall", "what": what, "share": round(len(close) / len(grid), 2)}
    hit = [g for g in grid if g[0] is not None and g[0] < CAM_FLAT_FAR]
    if grid and hit:
        top = max({g[1] for g in hit}, key=lambda n: sum(g[1] == n for g in hit))
        ds = [g[0] for g in hit if g[1] == top]
        mine = any(top == c or top.startswith(c + ".") for c in cast)
        if not mine and len(ds) >= CAM_FLAT * len(grid) and max(ds) < 1.5 * min(ds):
            # the back of a room's wall from outside it (ep105 S85: one wall 2 m off over the whole frame)
            return {"kind": "flat", "what": top, "share": round(len(ds) / len(grid), 2)}
    return None


def cam_problems(hits: list[dict], allow: list[str] | None = None) -> list[str]:
    """clipcheck's camera findings, one line per shot: story.json `cam_ok` (shot ids, or `<shot>/<object>`)
    leaves out a framing the story means (a shot through a car's own windscreen)."""
    by = {}
    for h in hits:
        if _allowed({"shot": h["shot"], "what": h["what"]}, allow):
            continue
        by.setdefault((h["shot"], h["kind"], h["what"].split(".")[0]), []).append(h["t"])
    out = []
    for (shot, kind, what), ts in by.items():
        when = f"{min(ts):.2f}-{max(ts):.2f} s" if len(ts) > 1 else f"{ts[0]:.2f} s"
        msg = {"inside": f"the camera is inside {what}", "wall": f"{what} fills the frame right in front of the lens",
               "flat": f"{what}, one flat surface, fills the whole frame"}[kind]
        out.append((min(ts), f"{shot} {when}: {msg} (blank frames: move the camera key)"))
    return [m for _, m in sorted(out)]


def _allowed(h: dict, allow) -> bool:
    """story.json `clip_ok`: entries are `<object>` (its name up to the first dot: "flap"), `<shot>` ("S36") or
    `<shot>/<object>`. An overlap the story means to have (a cat through its own flap, a face against the glass)."""
    what = h["what"].split(".")[0]
    for a in allow or []:
        sh, _, ob = a.partition("/")
        if (sh == h["shot"] and (not ob or ob == what)) or (not ob and sh == what):
            return True
    return False


def clip_problems(hits: list[dict], allow: list[str] | None = None, gap: float = 0.3) -> list[str]:
    """clipcheck's overlaps, one line per stretch: the shot, the seconds, whose head and what it passes through.
    Overlaps listed in `allow` (story.json `clip_ok`) are left out."""
    spans = {}
    for h in sorted((h for h in hits if not _allowed(h, allow)), key=lambda h: (h["who"], h["what"], h["t"])):
        k = (h["who"], h["what"])
        cur = spans.setdefault(k, [])
        if cur and h["t"] - cur[-1][2] <= gap and cur[-1][0] == h["shot"]:
            cur[-1][2] = h["t"]
        else:
            cur.append([h["shot"], h["t"], h["t"]])
    out = []
    for (who, what), ss in spans.items():
        for shot, a, b in ss:
            when = f"{a:.2f}-{b:.2f} s" if b > a else f"{a:.2f} s"
            out.append((a, f"{shot} {when}: {who}'s head passes through {what}"))
    return [m for _, m in sorted(out)]


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
    # hard rule 6: no music box. sound.py still has the voice for old tests, so a story naming it is blocked here
    # (ep89's proof qa caught it after every review missed it, 2026-11-03)
    voices = [v for sec in ((st.get("sound") or {}).get("music") or {}).get("sections", []) for v in sec.get("voices", [])]
    if "musicbox" in voices or "musicbox" in json.dumps(st.get("sound") or {}):
        out.append(("block", "the score uses the `musicbox` voice: RULES hard rule 6 says no music box. Use piano, pad or choir"))
    return out


ASSETS = Path(__file__).resolve().parent.parent / "assets"
TEXTURE_NAMES = ("brick", "wood", "concrete", "grass", "asphalt")   # kit.TEXTURES (kit needs bpy, so not imported)


def library(st: dict, set_text: str = "") -> list[tuple[str, str]]:
    """The CC0 library (assets/): a `look.hdri` must name a file in assets/hdri/, a set's kit.texture("x")
    one of the textures and its kit.prop("x") one of the props, so a typo shows up here and not as a plain world on the render."""
    out = []
    h = (st.get("look") or {}).get("hdri")
    if h and not (ASSETS / "hdri" / f"{h}.hdr").exists():
        have = sorted(p.stem for p in (ASSETS / "hdri").glob("*.hdr"))
        out.append(("block", f"look.hdri {h!r} isn't in assets/hdri/ (there are {have})"))
    names = json.loads((ASSETS / "props" / "props.json").read_text()) if (ASSETS / "props" / "props.json").exists() else {}
    for t in re.findall(r"kit\.prop\(\s*[\"']([^\"']+)", set_text):
        if t not in names:
            out.append(("block", f"set.py uses kit.prop({t!r}), which isn't in assets/props/props.json"))
    for t in re.findall(r"kit\.texture\(\s*[\"']([^\"']+)", set_text):
        if t not in TEXTURE_NAMES:
            out.append(("block", f"set.py uses kit.texture({t!r}); the textures are {TEXTURE_NAMES}"))
    return out


def polish_problems(st: dict) -> list[tuple[str, str]]:
    """look.polish (blocky/polish.py): known settings only, marked shots that exist, and a bed that's recorded."""
    from blocky import polish

    p = (st.get("look") or {}).get("polish")
    if not p or p is True:
        return []
    if not isinstance(p, dict):
        return [("block", "look.polish is true or a dict of settings")]
    out = [("block", f"look.polish.{k} isn't a polish setting ({sorted(polish.DEFAULTS)})") for k in p
           if k not in polish.DEFAULTS]
    ids = {s["id"] for s in st.get("shots", [])}
    if isinstance(p.get("sway"), list):
        out += [("block", f"look.polish.sway names shot {s!r}, which isn't in shots") for s in p["sway"] if s not in ids]
    if p.get("grade") and p["grade"] not in polish.GRADES:
        out.append(("block", f"look.polish.grade {p['grade']!r}: the presets are {sorted(polish.GRADES)}"))
    if p.get("bed_kind") and not (ASSETS / "audio" / "amb" / f"{p['bed_kind']}.wav").exists():
        out.append(("block", f"look.polish.bed_kind {p['bed_kind']!r} isn't a recording in assets/audio/amb/"))
    if not 0 <= float(p.get("punch", 0.06)) <= 0.08:
        out.append(("block", "look.polish.punch is a subtle 0 to 8% (0.0 to 0.08)"))
    return out


NARRATOR_MISFIT = re.compile(r"\bmy (husband|boyfriend|hubby)\b", re.I)   # the one narrator voice is a man's (ep38)


def lost_words(name: str, st: dict) -> list[str]:
    """Lines whose spoken words in story.json aren't the ones in the story's generator/lines.json (a caption
    splitter that dropped a word, ep115 L19): the narration reads story.json, so the lost word is never heard.
    `check` warns (it runs on every old story), `preflight` blocks."""
    from blocky import timeline

    src = STORIES / name / "generator" / "lines.json"
    if not src.exists():
        return []
    try:
        lines = json.loads(src.read_text())
    except ValueError:
        return []
    lines = lines.get("lines", []) if isinstance(lines, dict) else lines
    return timeline.lost_words(st, lines if isinstance(lines, list) else [])


def run(name: str, timeline: Path | None = None, st: dict | None = None) -> list[tuple[str, str]]:
    from blocky import voicecheck as sc

    from blocky import post

    st = st if st is not None else load_story(name)
    out = []
    set_py = STORIES / name / "set.py"   # tests pass in-memory stories with no folder
    if set_py.exists() and "flicker" in set_py.read_text() and not (st.get("look") or {}).get("flash_safe"):
        out.append(("warn", "the set has flickering lights but look.flash_safe isn't set; strobing flicker failed the "
                            "flash bar on most stories (RULES.md hard rule 7)"))
    if set_py.exists() and re.search(r"[\"'](/home/|/root/|/Users/|[A-Z]:\\\\)", set_py.read_text()):
        out.append(("block", "set.py uses a machine-specific absolute path (/home/..., /root/...): Actions has no such "
                             "folder, so every draw shard fails at once (ep58, 2026-11-03). Use tempfile or the story folder"))
    out += harsh_sound(st)
    out += library(st, set_py.read_text() if set_py.exists() else "")
    out += polish_problems(st)
    out += [("warn", f"spoken words differ from generator/lines.json (preflight blocks): {m}")
            for m in lost_words(name, st)]
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
            cuts = (len(tl["shots"]) - 1) / tl["duration"] * 10
            if cuts < CUTS_MIN_PER_10S:
                out.append(("warn", f"{cuts:.1f} cuts per 10 s; measure.py wants {CUTS_MIN_PER_10S:g} or more"))
            # pre-render craft: a still the final's measure would block on (preflight blocks on these)
            risks = still_risks(st, tl)
            if risks:
                out.append(("warn", f"{len(risks)} still(s) over {STILL_MAX_S:g} s by the edit alone (preflight blocks "
                                    f"on them), first: {risks[0]}"))
    return out
