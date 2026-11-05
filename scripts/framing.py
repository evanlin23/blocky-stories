"""Framing lint: does every shot show what its line is about? Report only, for now (rewrite plan step 8, C + N).

    python scripts/framing.py --story stories/<name> [--timeline t.json] [--json out.json] [--no-set]

Stories mostly drop on single shots that show the wrong thing while the line plays (docs/audit/lessons-log.md 26
and 32): the back of a head on a line about that person, an empty wall over "because you CALLED me", a crop of
hair over the shelf the line names, a head cut by the top of the frame, a face too small to read at phone size.
The stills sheet and the critic look at key beats; this looks at EVERY shot. It needs no Blender: the camera
comes from measure.cam_at (plus the polish pack's crop move and the punch-ins), each character from
acting.state, and the set's objects from set.py run against stand-ins (scripts/set_places.py).

The rig (blocky/rig.py): a character `h` tall (spec "height") has its head centred 1.57 h above its feet,
0.42 h wide and 0.41 h tall, and faces -y at yaw 0, so its face points along (sin(yaw + head_yaw), -cos(...)).

Who a line is about: the character who says it, every cast member the words name (the cast key without a trailing
number, or a spec's "aliases"), and, for a line with he / him / his / she / her and no name, the character named
in one of the four lines before (a he skips anyone whose key or aliases say grandma, mom, aunt...; a she, grandpa,
dad, uncle...). The narrator's own character ("me") is the subject of a line that says I, me or my only when it's
big on screen: then its face has to show (back or side), but it's never "missing" or "small".

The checks, sampled ten times a second over each (shot, line) overlap of 0.3 s or more. Each has to hold for
half the overlap or more. Calibrated 2026-11-05 against Blender's own head boxes and the reviews that dropped
ep109, ep112, ep115 and ep116 (docs/audit/lessons-log.md 34 and 37):
  cut      a head 1/12 of the width or bigger, with its hair and hat, 4% or more past an edge while 15% or
           more of it is still in: the top edge for anyone, the other three for the line's subject (the narrator
           on an I / me / my line too) or any face 0.18 of the width or more; or a head centred outside the frame that still covers 4% of it, or
           any of it when the head is 60% of the frame wide (a crop of hair at the lens). Once a shot.
  missing  the line is about X, and X's head is never in frame: always for a speaker, and for a character the
           words name when X is in the scene (unhidden, within 10 m of the camera during the line)
  back     X is in frame but the camera never sees X's face: 110 degrees or more off it, the back of the head;
           also, once a shot, on a he / she line its names don't reach, when no face is seen and the biggest
           head in frame (0.18 of the width or more) is turned away and can be that he or she (ep112 S26)
  side     ...70 to 110 degrees off it: a profile (a blocky face is drawn on the front of a round head, so at 70
           degrees it's gone: ep109 S52 was 67 to 76). A turned-away head under 1/12 of the width counts as small.
  small    X's face is seen but never 1/5 of the frame width (the owner's bar, less his 10% band: 0.18)
  empty    a voiced line about nobody in the cast, over a frame with no character, no creature (story.json
           "clip_heads"), no prop the words name and nothing prop-sized close by (an object 3 m or smaller,
           within 8 m, covering 3% of the frame): walls, floor and sky only
  tag      a seen face with the rule tag (what set.py hangs on the camera) over 30% of it, or over a third of
           an eye or of the mouth (ep116 S17), for half the shot. Once a shot.
  caption  a seen face 0.12 of the width or wider with a caption over half its mouth, during a line. Once a shot.
  hand     a hand (an arm's last block) nearer the camera than a seen face, with 30% of it over the face.
A shot in story.json "framing_ok": ["S12"] is skipped: a deliberate empty or back shot. A builder can name the
props the words mean in "framing_props": {"jar": [x, y, z]}, for a set.py this can't read.
It prints one row per finding and exits 0. Nothing blocks yet: wiring it into `check` or `gate` comes later.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
for _p in (str(ROOT), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import measure  # noqa: E402

U = 0.34                               # metres per rig unit, at height 1 (blocky/rig.py S)
HEAD_Z = U * (4.0 + 0.02 + 0.6)        # head centre above the feet: neck at 4, head 1.2 tall
HEAD_HALF_W = U * 0.62                 # faces.HEAD_R
HEAD_HALF_H = U * 0.6                  # faces.HEAD_H / 2

DT = 0.1             # ten samples a second
MIN_OVERLAP = 0.3    # a line under a shot for less than this is a cut landing, not a framing
SHARE = 0.5          # how much of the overlap a problem has to last
BIG = 0.2            # a face reads at phone size from 1/5 of the frame width (owner's bar, RULES.md)
BAND = 0.1           # ...with the owner's wiggle room (2026-11-03: "band can be like 10%"): small is under 0.18
CUT_MIN = 1 / 12     # a head narrower than this is background: cutting it doesn't count
CUT_OVER = 0.04      # 4% of the head (hair and hat included) past any edge is a cut head (ep115, ep116, ep109:
                     # reviewers drop heads 2 to 20% over the edge; 25% missed every one of them)
# what sits on top of the head, in its half heights (rig.py's boxes over the head's top, 0.6 units up)
HAIR_TOP = {"spiky": 0.78, "mop": 0.6, "bun": 0.5, "buzz": 0.05, "bald": 0.0}   # any other hair: 0.17
HAT_TOP = {"beanie": 0.65, "ballcap": 0.5, "tophat": 1.25, "bucket": 0.6, "hood": 0.3}   # any other hat: 0.5
HAIR_SIDE = 0.12     # ...and hair, brims and mustaches this much of the half width either side
CAP_MIN = 0.12       # a face this wide or wider has a mouth to read: the caption band check
MOUTH = (0.4, 0.3, 0.12)   # the mouth: drawn 0.4 hh under the head's centre (faces.py: 74% down the face box,
                           # the eyes 0.13 hh over the centre), 0.3 hw either side, 0.12 hh either way
CAP_OVER = 0.5       # a caption over half the mouth covers it
EYE_Y, EYE_X, EYE_R = 0.13, 0.32, 0.14   # each eye: 0.13 hh up, 0.32 hw either side, about 0.14 of each across
HAND_OVER = 0.3      # a hand box this much over a seen face, nearer the camera than the head, covers it
CROP_COVER = 0.04    # (a crop has to cover a quarter of this, 1% of the frame)
CROP_NEAR = 1.0      # a head centred outside the frame and wider than it, with any of it in: hair at the lens
FACE_DEG = 65.0      # the camera within this of the face's direction sees the face (80 passed ep109's S52, a
                     # profile at 67 to 76 degrees that its critic dropped: a face drawn on a round head is gone)
BACK_DEG = 110.0     # ...past this it sees the back of the head; in between, the side
PROP_MAX = 3.0       # an object this big or smaller (largest side, m) is a prop, not a wall
PROP_NEAR = 8.0      # ...within this of the camera (m)
PROP_COVER = 0.03    # ...covering this much of the frame
CARRY = 4           # a he / she with no name carries the last name from this many lines back
CROP_SHARE = 1 / 3   # a crop at the lens has to last this much of the shot (it's never deliberate)
NEAR = 10.0          # a named character within this of the camera (m), unhidden, near the line, is in the scene
AROUND = 0.0         # ...looking this far either side of the line (s): during the line itself
MAIN = 0.5           # a shot carrying this much of a line is its main shot: its subject has to be in it too
TAG_OVER = 0.3       # a face this much under the rule tag (set.py's HUD on the camera) is covered
PRONOUNS = re.compile(r"\b(he|him|his|she|her|hers)\b", re.I)
HE = re.compile(r"\b(he|him|his)\b", re.I)
SHE = re.compile(r"\b(she|her|hers)\b", re.I)
OTHER = {"m": "f", "f": "m"}
# who a he or a she can't be: a cast key, or an alias, with one of these words in it
FEMALE = {"mom", "mum", "mother", "ma", "grandma", "gran", "granny", "nana", "nan", "aunt", "auntie", "sister", "sis",
          "girl", "woman", "lady", "mrs", "ms", "miss", "wife", "daughter", "queen", "niece", "grandmother", "madam"}
MALE = {"dad", "father", "pa", "grandpa", "gramps", "grandad", "granddad", "uncle", "brother", "bro", "boy", "man",
        "guy", "mr", "husband", "son", "king", "nephew", "grandfather", "sir"}
SELF = re.compile(r"\b(i|me|my|mine|myself|i'm|i’m|i've|i’ve|i'd|i’d|i'll|i’ll)\b", re.I)
STOP = {"the", "and", "you", "your", "for", "with", "that", "this", "but", "not", "are", "was", "his", "her", "him",
        "she", "they", "them", "our", "out", "off", "all", "one", "two", "who", "what", "when", "then", "there",
        "here", "have", "has", "had", "its", "from", "into", "onto", "over", "under", "just", "still", "every",
        "never", "always", "back", "front", "top", "low", "left", "right", "big", "small", "new", "old", "now", "can",
        "body", "part", "side", "end", "base", "inner", "outer", "glow", "light", "fill", "rim", "key", "tag", "day",
        "way", "too", "yes", "say", "said", "says", "get", "got", "how", "why", "any", "each", "own", "set", "put"}


# ---------- words ----------

def words(text: str) -> set[str]:
    return {w.removesuffix("'s").removesuffix("’s") for w in re.findall(r"[a-z][a-z'’]*", text.lower())}


def stem(w: str) -> str:
    w = w.lower().removesuffix("'s").removesuffix("’s")
    if len(w) > 4 and w.endswith("ves"):
        return w[:-3] + "f"
    if len(w) > 4 and w.endswith("ies"):
        return w[:-3] + "y"
    if len(w) > 4 and w.endswith(("ses", "xes", "ches", "shes")):
        return w[:-2]
    if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
        return w[:-1]
    return w


def tokens(name: str) -> set[str]:
    """An object name's words: "shelf3.box_lid" -> {"shelf", "box", "lid"} (3 letters or more, no stop words)."""
    return {stem(t) for t in re.findall(r"[a-z]+", name.lower()) if len(t) >= 3 and t not in STOP}


def names_of(cast: dict) -> dict[str, frozenset]:
    """Each name the words can use -> the cast members it fits. A key without its trailing number ("uncle2" is
    "uncle": the same person, rigged twice), the last part of an underscored key ("mrs_kettle" is "kettle"), and a
    spec's "aliases". The narrator's own character ("me", "me2") is never named: "me" is in every other line."""
    out: dict[str, set] = {}
    for k, v in cast.items():
        base = re.sub(r"\d+$", "", k.lower())
        if base == "me" or v.get("offscreen"):
            continue
        ns = {base, base.split("_")[-1]} | {a.lower() for a in v.get("aliases", [])}
        for n in ns:
            if len(n) > 2 and n not in STOP:
                out.setdefault(n, set()).add(k)
    return {n: frozenset(ks) for n, ks in out.items()}


def sex_of(group, cast: dict) -> str | None:
    """"f" or "m" when every member's key or aliases say so (grandma, uncle2, "aliases": ["mrs kettle"]), else None."""
    out = set()
    for k in group:
        ws = set(re.findall(r"[a-z]+", " ".join([k.lower(), *[a.lower() for a in cast.get(k, {}).get("aliases", [])]])))
        out.add("f" if ws & FEMALE and not ws & MALE else "m" if ws & MALE and not ws & FEMALE else None)
    return out.pop() if len(out) == 1 else None


def self_lines(st: dict, tl: dict) -> dict[str, frozenset]:
    """Line id -> the narrator's own character, for a voiced line that says I, me or my and isn't its own: there
    the narrator is the subject when on screen, so the facing test applies (ep109 S52: me in profile on my own
    "I finally said sorry"). Never "missing" or "small": I is in nearly every line."""
    mes = frozenset(k for k, v in st.get("cast", {}).items()
                    if re.sub(r"\d+$", "", k.lower()) == "me" and not v.get("offscreen"))
    if not mes:
        return {}
    return {lid: mes for lid in tl["order"] if tl["lines"][lid]["who"] not in ("pause", *mes)
            and SELF.search(tl["lines"][lid].get("text", ""))}


def about(st: dict, tl: dict) -> dict[str, list[frozenset]]:
    """Line id -> who it's about, the speaker first: each one a group of cast members (any of them on screen will
    do), from the speaker, the names in the words, or a he / she that carries a name from the four lines before."""
    cast = {k: v for k, v in st.get("cast", {}).items() if not v.get("offscreen")}
    names = names_of(cast)
    out, recent = {}, []
    for lid in tl["order"]:
        ln = tl["lines"][lid]
        if ln["who"] == "pause":
            continue
        text = ln.get("text", "")
        ws = words(text)
        named = []
        for n, ks in names.items():
            if n in ws and ks not in named:
                named.append(ks)
        if not named and PRONOUNS.search(text):
            sex = "f" if SHE.search(text) and not HE.search(text) else "m" if HE.search(text) and not SHE.search(text) \
                else None
            fits = [g for p in reversed(recent[-CARRY:]) for g in p if sex is None or sex_of(g, cast) != OTHER[sex]]
            named = fits[:1]
        who = [frozenset([ln["who"]])] if ln["who"] in cast else []
        out[lid] = who + [g for g in named if not (who and who[0] <= g)]
        recent.append(named)
    return out


# ---------- the picture ----------

def to_frame(p, crop):
    """A projected point (measure.project: x, y in -1..1) through the output crop: zoom z, slid by (dx, dy)."""
    z, dx, dy = crop
    return (p[0] - 2 * dx) * z, (p[1] - 2 * dy) * z


def head_view(loc, tgt, lens, s, spec, crop):
    """Character state s's head in the frame: centre x, y and half extents hw, hh (-1..1 units), width (fraction
    of the frame width) and ang (degrees between the face's direction and the camera). None behind the camera."""
    h = float(spec.get("height", 1.0))
    wd = float(spec.get("width", 1.0))
    c = np.array([s["x"], s["y"], s["z"] + HEAD_Z * h])
    p = measure.project(loc, tgt, lens, c)
    if p is None:   # behind the camera: nowhere in frame, but still this far away
        return {"x": math.inf, "y": math.inf, "hw": 0.0, "hh": 0.0, "width": 0.0, "ang": 180.0,
                "dist": float(np.linalg.norm(c - np.asarray(loc, float)))}
    x, y = to_frame(p, crop)
    per_m = p[2] * crop[0]                         # fraction of the frame width per metre
    hw = 2 * HEAD_HALF_W * h * wd * per_m           # -1..1 spans the frame, so a half extent = a width fraction
    hh = 2 * HEAD_HALF_H * h * per_m * 1080 / 1920
    yaw = s["yaw"] + s["head_yaw"]
    face = np.array([math.sin(yaw), -math.cos(yaw)])
    to_cam = np.asarray(loc[:2], float) - c[:2]
    n = float(np.linalg.norm(to_cam))
    ang = 0.0 if n < 1e-6 else math.degrees(math.acos(float(np.clip(face @ to_cam / n, -1, 1))))
    hat = spec.get("hat", "none")
    top = HAT_TOP.get(hat, 0.5) if hat not in (None, "none", "") else HAIR_TOP.get(spec.get("hair", "cap"), 0.17)
    return {"x": x, "y": y, "hw": hw, "hh": hh, "width": hw, "ang": ang,
            "top": hh * (1 + top), "side": hw * (1 + HAIR_SIDE),
            "dist": float(np.linalg.norm(c - np.asarray(loc, float)))}


def body_points(s, spec):
    """The torso, hips, shoulders and hands, in the world (m)."""
    h = float(spec.get("height", 1.0)) * U
    yaw = s["yaw"]
    right = np.array([math.cos(yaw), math.sin(yaw), 0.0])
    fwd = np.array([math.sin(yaw), -math.cos(yaw), 0.0])
    base = np.array([s["x"], s["y"], s["z"]])
    up = np.array([0, 0, 1.0])
    pts = [base + up * 3.0 * h, base + up * 1.5 * h]
    for side, arm in zip((-1, 1), s["arms"]):
        sh = base + up * 3.75 * h + right * side * 1.5 * h
        pts += [sh, sh + (fwd * math.sin(arm) - up * math.cos(arm)) * 2.0 * h]
    return pts


def point_in(loc, tgt, lens, q, crop) -> bool:
    p = measure.project(loc, tgt, lens, np.asarray(q, float))
    if p is None:
        return False
    x, y = to_frame(p, crop)
    return abs(x) <= 1 and abs(y) <= 1


def in_frame(v) -> bool:
    return v is not None and abs(v["x"]) <= 1 and abs(v["y"]) <= 1


def cover(v) -> float:
    """How much of the frame a head's box covers (0..1)."""
    if v is None:
        return 0.0
    w = max(0.0, min(1, v["x"] + v["hw"]) - max(-1, v["x"] - v["hw"]))
    h = max(0.0, min(1, v["y"] + v["hh"]) - max(-1, v["y"] - v["hh"]))
    return w * h / 4


def cut_edge(v) -> str | None:
    """The edge that cuts this head, or None. A head the frame's width or wider with 1% of the frame in is a crop
    (hair at the lens); otherwise a head 1/12 of the width or bigger is cut when between 15% and 75% of it is in
    frame (a quarter or more past an edge, but still there to see)."""
    if v is None:
        return None
    over = {"top": v["y"] + v["hh"] - 1, "bottom": -1 - (v["y"] - v["hh"]),
            "right": v["x"] + v["hw"] - 1, "left": -1 - (v["x"] - v["hw"])}
    c = cover(v)
    if v["width"] >= CROP_NEAR:
        return "crop:" + max(over, key=over.get) if c >= CROP_COVER / 4 else None
    if v["width"] < CUT_MIN or c <= 0:
        return None
    seen = c * 4 / (4 * v["hw"] * v["hh"])
    if seen < 0.15:   # hardly there: a head leaving the frame, not a framing
        return None
    # the head with its hair and hat, against each of the four edges: the share of it past that edge
    top, side = v.get("top", v["hh"]), v.get("side", v["hw"])
    past = {"top": (v["y"] + top - 1) / (v["hh"] + top), "bottom": (-1 - (v["y"] - v["hh"])) / (v["hh"] + top),
            "right": (v["x"] + side - 1) / (2 * side), "left": (-1 - (v["x"] - side)) / (2 * side)}
    e = max(past, key=past.get)
    return e if past[e] >= CUT_OVER else None


def overlap(a, b) -> float:
    """The area two boxes (x0, y0, x1, y1) share."""
    return max(0.0, min(a[2], b[2]) - max(a[0], b[0])) * max(0.0, min(a[3], b[3]) - max(a[1], b[1]))


def area(a) -> float:
    return max(0.0, a[2] - a[0]) * max(0.0, a[3] - a[1])


def seen_face(v) -> bool:
    return v is not None and in_frame(v) and v["ang"] <= FACE_DEG and v["width"] >= CUT_MIN


def face_box(v):
    return (v["x"] - v["hw"], v["y"] - v["hh"], v["x"] + v["hw"], v["y"] + v["hh"])


def mouth_box(v):
    y = v["y"] - MOUTH[0] * v["hh"]
    return (v["x"] - MOUTH[1] * v["hw"], y - MOUTH[2] * v["hh"], v["x"] + MOUTH[1] * v["hw"], y + MOUTH[2] * v["hh"])


def eye_boxes(v):
    y = v["y"] + EYE_Y * v["hh"]
    return [(v["x"] + s * EYE_X * v["hw"] - EYE_R * v["hw"] * 2, y - EYE_R * v["hh"] * 2,
             v["x"] + s * EYE_X * v["hw"] + EYE_R * v["hw"] * 2, y + EYE_R * v["hh"] * 2) for s in (-1, 1)]


def under_tag(v, tag) -> bool:
    """Is a seen face (a head in frame, facing the camera) under the tag's box: TAG_OVER or more of it, or a third
    of an eye or of the mouth (ep116 S17: the tag over one eye, 13% of the face)?"""
    if tag is None or not seen_face(v):
        return False
    if overlap(tag, face_box(v)) >= TAG_OVER * area(face_box(v)):
        return True
    return any(overlap(tag, b) >= area(b) / 3 for b in [*eye_boxes(v), mouth_box(v)])


def hand_boxes(loc, tgt, lens, s, spec, crop):
    """Each hand's box in the frame and its distance from the camera: the last block of each arm (rig.py: arms 2
    long from the shoulder, raised forward by `arms`, out by `side`), a 1-unit cube."""
    h = float(spec.get("height", 1.0)) * U
    yaw = s["yaw"]
    right = np.array([math.cos(yaw), math.sin(yaw), 0.0])
    fwd = np.array([math.sin(yaw), -math.cos(yaw), 0.0])
    up = np.array([0, 0, 1.0])
    base = np.array([s["x"], s["y"], s["z"]])
    out = []
    for side, arm, out_ in zip((-1, 1), s["arms"], s.get("arms_side", (0.0, 0.0))):
        sh = base + up * 3.75 * h + right * side * 1.5 * h
        d = (fwd * math.sin(arm) - up * math.cos(arm)) * math.cos(out_) + right * side * math.sin(out_)
        c = sh + d * 1.6 * h
        p = measure.project(loc, tgt, lens, c)
        if p is None:
            continue
        x, y = to_frame(p, crop)
        hw = 0.5 * h * p[2] * crop[0] * 2
        hh = hw * 1080 / 1920
        out.append(((x - hw, y - hh, x + hw, y + hh), float(np.linalg.norm(c - np.asarray(loc, float)))))
    return out


_CAPS: dict = {}


def caption_box(c) -> tuple | None:
    """A caption's block in the frame (x0, y0, x1, y1 in -1..1, y up), from post.caption_image's own layout."""
    k = (c["text"], bool(c.get("big")))
    if k not in _CAPS:
        try:
            from blocky import post
            _, m = post.caption_image(c["text"], c.get("big", False))
            w, h = m["w"], m["h"]
            x0, y0 = post.CX - w / 2, post.CY - h / 2
            pad = 15   # caption_image's 30 px of padding, top and bottom together
            _CAPS[k] = (x0 / 540 - 1, 1 - 2 * (y0 + h - pad) / 1920, (x0 + w) / 540 - 1, 1 - 2 * (y0 + pad) / 1920)
        except Exception:   # noqa: BLE001 - no font or PIL: the band the one-line captions use (62 to 69%)
            _CAPS[k] = (-0.6, -0.38, 0.55, -0.25)
    return _CAPS[k]


def box_view(loc, tgt, lens, c, half, crop):
    """(in frame?, share of the frame covered, distance) for a box (centre, half size), from its 8 corners."""
    c, half = np.asarray(c, float), np.asarray(half, float)
    xs, ys = [], []
    for a in (-1, 1):
        for b in (-1, 1):
            for d in (-1, 1):
                p = measure.project(loc, tgt, lens, c + np.array([a, b, d]) * half)
                if p is None:
                    continue
                x, y = to_frame(p, crop)
                xs.append(x)
                ys.append(y)
    if not xs:
        return False, 0.0, 0.0
    x0, x1 = max(-1, min(xs)), min(1, max(xs))
    y0, y1 = max(-1, min(ys)), min(1, max(ys))
    if x1 < x0 or y1 < y0:
        return False, 0.0, 0.0
    return True, (x1 - x0) * (y1 - y0) / 4, float(np.linalg.norm(c - loc))


# ---------- the set ----------

class Places:
    """set.py's objects at time t, cached, through scripts/set_places.py; empty when there's no set.py or the
    stand-ins can't run it (`why` says which)."""

    def __init__(self, story_dir: Path | None, st: dict, tl: dict):
        self.sp, self.why, self.cache = None, "no set.py", {}
        if story_dir is None or not (Path(story_dir) / "set.py").exists():
            return
        try:
            import set_places
            self.sp = set_places.SetPlaces(Path(story_dir), st, copy.deepcopy(tl))
            self.why = None
        except Exception as e:   # noqa: BLE001 - any set.py: lint without props rather than not at all
            self.why = f"set.py didn't run: {type(e).__name__}: {str(e)[:60]}"

    def names(self) -> set[str]:
        return {o.name for o in self.sp.objs} if self.sp else set()

    def hud(self, t: float, lens: float, crop) -> tuple | None:
        """The tag's box in the frame at t (one box round all of it, through the crop), or None."""
        if self.sp is None:
            return None
        self.at(t)
        if self.sp.error:   # animate() didn't run, so the tag was never put in its place
            return None
        bs = self.sp.hud(lens)
        if not bs:
            return None
        z, dx, dy = crop
        x0, y0 = min(b[0] for b in bs), min(b[1] for b in bs)
        x1, y1 = max(b[2] for b in bs), max(b[3] for b in bs)
        if (x1 - x0) * (y1 - y0) / 4 > 0.25:   # not a tag: something parked on the camera, or a stand-in's guess
            return None
        return ((x0 - 2 * dx) * z, (y0 - 2 * dy) * z, (x1 - 2 * dx) * z, (y1 - 2 * dy) * z)

    def at(self, t: float) -> dict:
        if self.sp is None:
            return {}
        k = round(t, 2)
        if k not in self.cache:
            self.cache[k] = self.sp.at(t)
        return self.cache[k]


# ---------- the lint ----------

def lint(st: dict, tl: dict, story_dir: Path | None = None, use_set: bool = True) -> tuple[list[dict], dict]:
    from blocky import acting, polish, post
    from blocky import timeline as T
    cast = {k: v for k, v in st.get("cast", {}).items() if not v.get("offscreen")}
    ok = set(st.get("framing_ok", []))
    props = {k.lower(): v for k, v in st.get("framing_props", {}).items()}
    pol = polish.spec(st)
    specs = polish.cam_specs(st, tl, pol)
    at = T.resolver(tl["lines"], tl["duration"])
    emph = polish.emph_times(tl, pol, at) if pol else []
    lines_about = about(st, tl)
    selves = self_lines(st, tl)
    places = Places(story_dir if use_set else None, st, tl)
    heads = tuple(st.get("clip_heads", []))
    voiced = [l for l in tl["order"] if tl["lines"][l]["who"] != "pause"]
    tok = {n: tokens(n) for n in places.names()}
    named, said = {}, {}
    for lid in voiced:
        ws = {stem(w) for w in words(tl["lines"][lid].get("text", ""))} - STOP
        said[lid] = ws
        named[lid] = {n for n, tk in tok.items() if tk & ws}

    def crop(t):
        z = post.fx_at(tl, t)["punch"]
        if not pol:
            return z, 0.0, 0.0
        pz, dx, dy = polish.motion(tl, st, pol, t, emph)
        return z * pz, dx, dy

    def something(loc, tgt, lens, cr, t, lid) -> bool:
        """A creature, a prop the line names, or anything prop-sized close by, in frame at t."""
        for pn, pos in props.items():
            if pn in said[lid] and point_in(loc, tgt, lens, pos, cr):
                return True
        for n, (c, half) in places.at(t).items():
            if 2 * float(np.max(half)) > PROP_MAX and n not in named[lid] and not (heads and n.startswith(heads)):
                continue
            seen, share, dist = box_view(loc, tgt, lens, c, half, cr)
            if seen and (n in named[lid] or (heads and n.startswith(heads))
                         or (share >= PROP_COVER and dist <= PROP_NEAR)):
                return True
        return False

    rows, shot_samples, line_shots, tags, hands = [], {}, [], {}, {}
    caps = tl.get("captions", [])
    for shot in tl["shots"]:
        sid = shot["id"]
        spec = specs.get(sid, {})
        if sid in ok or "cam" not in spec:
            continue
        ts = np.arange(shot["start"], shot["end"] - 1e-6, DT)
        if not len(ts):
            ts = np.array([shot["start"]])
        samples = []   # (t, camera, crop, {who: head view}, someone's body in frame)
        for t in map(float, ts):
            loc, tgt, lens = measure.cam_at(spec, shot, t, tl)
            cr = crop(t)
            vs, body = {}, False
            for name, cs in cast.items():
                s = acting.state(tl, name, t)
                if s["hidden"]:
                    vs[name] = None
                    continue
                vs[name] = head_view(loc, tgt, lens, s, cs, cr)
                hands[(sid, t, name)] = hand_boxes(loc, tgt, lens, s, cs, cr)
                body = body or in_frame(vs[name]) or cover(vs[name]) > 0 or \
                    any(point_in(loc, tgt, lens, q, cr) for q in body_points(s, cs))
            samples.append((t, (loc, tgt, lens), cr, vs, body))
            tags[(sid, t)] = places.hud(t, lens, cr)
        lids = [l for l in voiced
                if min(shot["end"], tl["lines"][l]["end"]) - max(shot["start"], tl["lines"][l]["onset"]) >= MIN_OVERLAP]

        shot_samples[sid] = samples
        line_shots += [(lid, sid) for lid in lids]
        where = ",".join(lids) or "-"

        def once(check, name, bad, what, share=SHARE):
            """A finding, once a shot, when `bad` holds for `share` or more of its samples."""
            if bad and len(bad) >= share * len(samples):
                rows.append(row(sid, shot["start"], shot["end"], where, check, name, what))
                return True
            return False

        # cut heads and crops, once a shot: the top edge for anyone; a side or the bottom for the line's subject
        # (the narrator's own character on an I / me / my line too) or any main face, 0.18 of the width or more
        # (a passer-by at the edge, or an extra in a crowd, is composition)
        subj = {n for l in lids for g in lines_about.get(l, []) + [selves.get(l, frozenset())] for n in g}
        for name in cast:
            hit = [e for e, v in ((cut_edge(x[3][name]), x[3][name]) for x in samples) if e and (
                e == "top" or e.startswith("crop:") or name in subj or v["width"] >= BIG * (1 - BAND))]
            crops = [e for e in hit if e.startswith("crop:")]
            if (hit and len(hit) >= SHARE * len(samples)) or len(crops) >= CROP_SHARE * len(samples):
                e = max(set(crops if len(crops) >= CROP_SHARE * len(samples) else hit), key=hit.count)
                what = f"a crop of the head fills the frame ({e[5:]} edge)" if e.startswith("crop:") else \
                    f"head cut by the {e} edge"
                rows.append(row(sid, shot["start"], shot["end"], where, "cut", name, what))

        for name in cast:   # a face under the rule tag, anyone's, once a shot
            once("tag", name, [x for x in samples if under_tag(x[3].get(name), tags.get((sid, x[0])))],
                 f"the tag over an eye, the mouth or {TAG_OVER:.0%} of the face")

        def hand_over(x, name):
            """Anyone's hand nearer the camera than this seen face, and HAND_OVER of the hand over it."""
            v = x[3].get(name)
            if not seen_face(v):
                return False
            return any(d < v["dist"] and overlap(b, face_box(v)) >= HAND_OVER * area(b)
                       for o in cast for b, d in hands.get((sid, x[0], o), []))

        for name in cast:   # a hand in front of a face
            once("hand", name, [x for x in samples if hand_over(x, name)], "a hand over the face")

        def under_caption(x, name):
            v = x[3].get(name)
            if not seen_face(v) or v["width"] < CAP_MIN:
                return False
            box = mouth_box(v)
            return any(c["start"] <= x[0] < c["end"] and overlap(caption_box(c), box) >= CAP_OVER * area(box)
                       for c in caps)

        if lids:   # a caption over a mouth, while someone speaks
            for name in cast:
                once("caption", name, [x for x in samples if under_caption(x, name)],
                     "mouth in the caption band (the caption over half of it)")

        def only_back(x):
            """No face seen, and the biggest head in frame is turned away and big: the back of a head is the shot."""
            vs = [v for v in x[3].values() if v is not None and in_frame(v) and v["width"] >= CUT_MIN]
            if not vs or any(v["ang"] <= FACE_DEG for v in vs):
                return False
            big = max(vs, key=lambda v: v["width"])
            return big["ang"] >= BACK_DEG and big["width"] >= BIG * (1 - BAND)

        # ...on a he or a she that can be them (ep112 S26, "He said nobody ever looks at the guy": a line the
        # names don't reach, over the back of the man it's about). A back on a line about someone else, or no one,
        # is a walk away, a look out of the window: passed films are full of them.
        hes = [tl["lines"][l].get("text", "") for l in lids if PRONOUNS.search(tl["lines"][l].get("text", ""))]
        backs = [x for x in samples if only_back(x)] if hes else []
        if backs:
            who = max((n for n in cast if backs[0][3].get(n) is not None and in_frame(backs[0][3][n])),
                      key=lambda n: backs[0][3][n]["width"])
            sx = sex_of(frozenset([who]), cast)
            fits = any((HE.search(t) and sx != "f") or (SHE.search(t) and sx != "m") for t in hes)
            if fits and not any(who in g for l in lids for g in lines_about.get(l, [])):
                once("back", who, backs, "the only head in frame shows its back, on a he / she")

        for lid in lids:
            ln = tl["lines"][lid]
            if lines_about.get(lid):
                continue
            a, b = max(shot["start"], ln["onset"]), min(shot["end"], ln["end"])
            win = [x for x in samples if a - 1e-6 <= x[0] < b] or samples[:1]
            a, b = max(shot["start"], ln["onset"]), min(shot["end"], ln["end"])
            win = [x for x in samples if a - 1e-6 <= x[0] < b] or samples[:1]
            empty = [not body and not something(*cam, cr, t, lid) for t, cam, cr, _, body in win]
            if sum(empty) >= SHARE * len(win):
                rows.append(row(sid, a, b, lid, "empty", "-", "no character or named prop in frame"))

    # the line's subject, over the whole line: never in frame (missing), in frame but the face never seen (back),
    # the face seen but never 1/5 of the width (small). Reported on each of the line's shots.
    def present(group, a, b) -> bool:
        """Is anyone in the group in the scene around a..b: unhidden and near the camera at some sample?"""
        for sid, xs in shot_samples.items():
            for x in xs:
                if a - AROUND <= x[0] < b + AROUND:
                    if any(x[3].get(n) is not None and x[3][n]["dist"] <= NEAR for n in group):
                        return True
        return False

    def judge(group, win, speaks=True, a=0.0, b=0.0):
        vs = [x[3][n] for x in win for n in group if n in x[3]]
        inside = [v for v in vs if v is not None and cover(v) > 0]   # any of the head in frame (a cut one too)
        faces = [v for v in inside if v["ang"] <= FACE_DEG]
        if not inside:
            # a speaker always has to be seen; a character the words name, only when they're in the scene
            # (a narrator talking about someone away, or long gone, over other pictures is the story)
            if not speaks and not present(group, a, b):
                return None
            return "missing", "not in frame"
        if not faces:
            best = max(v["width"] for v in inside)
            if best < CUT_MIN:
                return "small", f"far off and turned away (head {best:.2f} of the width)"
            ang = min(v["ang"] for v in inside)
            kind = "back" if ang >= BACK_DEG else "side"
            return kind, f"face never seen ({ang:.0f} deg or more off it)"
        if max(v["width"] for v in faces) < BIG * (1 - BAND):
            return "small", f"face {max(v['width'] for v in faces):.2f} of the width at best (bar 0.20)"
        return None

    for lid in voiced:
        ln = tl["lines"][lid]
        shots_ = [s for l, s in line_shots if l == lid]
        if not shots_:
            continue
        span = ln["end"] - ln["onset"]
        cut_at = {sid: next(s for s in tl["shots"] if s["id"] == sid) for sid in shots_}
        for group in lines_about.get(lid, []):
            name = "/".join(sorted(group))
            role = "speaks" if ln["who"] in group else "named"
            sp = ln["who"] in group
            whole = judge(group, [x for sid in shots_ for x in shot_samples[sid] if ln["onset"] - 1e-6 <= x[0] < ln["end"]],
                          sp, ln["onset"], ln["end"])
            if whole:   # the whole line fails: one row, over all its shots
                ids = [sid for sid in shots_]
                a = max(cut_at[ids[0]]["start"], ln["onset"])
                b = min(cut_at[ids[-1]]["end"], ln["end"])
                rows.append(row(ids[0] if len(ids) == 1 else f"{ids[0]}-{ids[-1]}", a, b, lid, whole[0], name,
                                f"{role}, {whole[1]}"))
                continue
            for sid in shots_:
                sh = cut_at[sid]
                a, b = max(sh["start"], ln["onset"]), min(sh["end"], ln["end"])
                if b - a < MAIN * span:
                    continue
                verdict = judge(group, [x for x in shot_samples[sid] if a - 1e-6 <= x[0] < b], sp, ln["onset"], ln["end"])
                if verdict:   # the line's main shot has to show them too
                    rows.append(row(sid, a, b, lid, verdict[0], name,
                                    f"{role}, {verdict[1]} in its main shot ({(b - a) / span:.0%} of the line)"))
        me = selves.get(lid)
        if me and not any(me & g for g in lines_about.get(lid, [])):
            for sid in shots_:   # the narrator on screen on their own I / me / my line: the face has to show
                sh = cut_at[sid]
                a, b = max(sh["start"], ln["onset"]), min(sh["end"], ln["end"])
                if b - a < MAIN * span:
                    continue
                vs = [x[3][n] for x in shot_samples[sid] if a - 1e-6 <= x[0] < b for n in me if n in x[3]]
                inside = [v for v in vs if v is not None and in_frame(v) and v["width"] >= BIG * (1 - BAND)]
                if inside and len(inside) >= SHARE * len(vs) and not any(v["ang"] <= FACE_DEG for v in inside):
                    ang = min(v["ang"] for v in inside)
                    rows.append(row(sid, a, b, lid, "back" if ang >= BACK_DEG else "side", "/".join(sorted(me)),
                                    f"self (I / me / my), face never seen ({ang:.0f} deg or more off it) in its "
                                    f"main shot ({(b - a) / span:.0%} of the line)"))

    rows.sort(key=lambda r: (r["t0"], r["check"]))
    info = {"props": "set.py" if places.sp else (places.why if use_set else "off"),
            "animate": (places.sp.error or "ok") if places.sp else None}
    return rows, info


def row(shot, a, b, line, check, who, detail):
    return {"shot": shot, "t0": round(a, 2), "t1": round(b, 2), "line": line, "check": check, "who": who,
            "detail": detail}


def counts(rows: list[dict]) -> dict:
    c = {}
    for r in rows:
        c[r["check"]] = c.get(r["check"], 0) + 1
    return c


def table(rows: list[dict]) -> str:
    out = ["| shot | seconds | line | check | who | detail |", "|---|---|---|---|---|---|"]
    out += [f"| {r['shot']} | {r['t0']:.1f}-{r['t1']:.1f} | {r['line']} | {r['check']} | {r['who']} | {r['detail']} |"
            for r in rows]
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--story", type=Path, required=True)
    ap.add_argument("--timeline", type=Path)
    ap.add_argument("--json", type=Path)
    ap.add_argument("--no-set", action="store_true", help="don't read set.py (faster; no props)")
    a = ap.parse_args(argv)
    st, tl = measure.load_timeline(a.story, a.timeline)
    if tl is None:
        print(f"{a.story}: no voice-timings.json and no --timeline: nothing to check")
        return 0
    rows, info = lint(st, tl, a.story, not a.no_set)
    print(f"# framing: {st.get('name', a.story.name)}: {len(tl['shots'])} shots, {len(rows)} findings "
          f"{counts(rows)} (props: {info['props']}{'; ' + info['animate'] if info.get('animate') not in (None, 'ok') else ''})")
    if rows:
        print(table(rows))
    if a.json:
        a.json.write_text(json.dumps({"story": st.get("name"), "findings": rows, "counts": counts(rows), **info},
                                     indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
