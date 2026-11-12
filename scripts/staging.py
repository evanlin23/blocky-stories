"""Staging lint: lurches, bodies standing inside each other (lesson 46) and body flips. Report-only.

    python scripts/staging.py --story stories/<name> [--timeline t.json] [--json out.json]

Three merged stories needed a fix round after the final for staging the story files alone could show
(2026-11-06): ep122 S56 (a hold key at the walk's start against a walk to the other side: the legs jumped 0.7 m
in 4 frames), ep125 (an acting key 0.067 s after a hold 0.6 m away: a 0.6 m jump in 2 frames) and ep132 (two
people 0.85 m apart, arm to arm through each other; one merged block on the cover). Reviews look at stills and
the proof qa at a contact sheet, so neither sees a 2-frame jump or arms inside arms. This reads every frame of
the edit, with no Blender: each character from blocky.acting.state, the camera from the shot's keys with the
polish pack's move (polish.cam_specs, checks._cam_at), as `check`'s still spans do.

  lurch   a character's root moves more than LURCH_M (0.25 m) within LURCH_S (0.15 s), seen where it starts and
          where it lands, and not as a walk or a run. A walk or a run is a pos segment of MOVE_MIN_S (0.4 s) or
          more: acting.state opens the leg swing over 0.15 s at each end of a segment, so a shorter one slides
          the body with its legs nearly still (both lurches above), and two keys at one time with different places
          jump with no segment at all. Speed alone isn't a lurch: a 7 m/s sprint over a second has its legs going.
          Only the motion inside a shot counts: a cut can move anyone anywhere (stories keep their sets 100 m
          apart and move the cast between them on cuts), except when the camera stays where it was (within
          SAME_CAM_M, lens within 15%) and the character is seen on both sides: a jump cut.
  close   two visible characters in the same shot, on the same frame, whose root centres (on the ground) are
          closer than CLOSE_M (1.35 m, a default character arm to arm) times the average of their widths
          (spec height x width x body_width), AND whose footprints overlap: each a box HALF_W (0.68 m) either
          side of the root along the shoulders and HALF_D (0.17 m, half the torso) front and back, plus what a
          raised or outstretched arm reaches. Side by side under 1.35 m their arms pass through each other, and at
          phone size two read as one block (ep132); face to face at 0.8 m nobody touches (a body is 0.34 m deep).
  yaw     a character's body yaw turns more than YAW_DEG (45 degrees) within YAW_F (2) frames inside one shot, seen
          on both frames: a flip or a spin, not a turn (ep125 S39, Lou 153 degrees in one frame; S42, the legs
          spinning 300 degrees from a key written 305 instead of -55). The turn is measured as drawn: each frame's
          step taken the short way round (a key 360 degrees from the last doesn't count), then summed.

On camera: the head or any of the torso, hips, shoulders or hands (scripts/framing.py's body points) inside the
frame, the body at least MIN_SIZE (5%) of the frame's width (not a speck 100 m off), not hidden, and not an
"offscreen" cast member. Walls are not known here: a character behind one still counts. Deliberate contact (a hug, a hand-hold, two people in a
photo booth) goes in story.json `"staging_ok": ["S12/hug", "S14", "S20/me+mom", "S30/dad"]`: a shot, a shot and a
note after the slash (anything that isn't a cast key, kept as the reason), a shot and a pair, or a shot and one
character (both checks for that character in that shot). Prints frame, time, shot and characters for each
finding. Exit 1 on any finding, 0 on none.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
for _p in (str(ROOT), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import framing  # noqa: E402
import measure  # noqa: E402

LURCH_M = 0.25      # metres...
LURCH_S = 0.15      # ...within this many seconds is a jump, not a step
MOVE_MIN_S = 0.4    # a walk or a run keyed over at least this long is a move; shorter is a jump
MIN_SIZE = 0.05     # a character narrower than this share of the frame is a speck in the distance, not on camera
SAME_CAM_M = 0.5    # a cut whose camera and target both move less than this (and its lens under 15%) is the same view
CLOSE_M = 1.35      # a default character arm to arm (4 rig units of 0.34 m)
HALF_W = 0.68       # half of that: the shoulder line with the arms down, either side of the root
HALF_D = 0.17       # half the torso's depth (1 unit), front to back
ARM = 0.68          # an arm's length (2 units): how far a raised arm reaches forward, or out to the side
FOOT_PAD = 0.02     # a touch isn't a hit: the boxes have to overlap by more than this, all round
YAW_DEG = 45.0      # a body turning more than this many degrees...
YAW_F = 2           # ...within this many frames is a flip, not a turn


def width(spec: dict) -> float:
    """How wide the character is arm to arm, as a multiple of a default character."""
    return float(spec.get("height", 1.0)) * float(spec.get("width", 1.0)) * float(spec.get("body_width", 1.0))


def _shot(tl: dict, f: int) -> dict:
    for s in tl["shots"]:
        if s["f0"] <= f < s["f1"]:
            return s
    return tl["shots"][-1]


def _move_ok(seg) -> bool:
    """A pos segment long enough for a walk or a run: acting.state opens the leg swing over 0.15 s at each end,
    so a segment under MOVE_MIN_S slides the body with its legs nearly still (ep122, ep125)."""
    return bool(seg) and seg[1]["t"] - seg[0]["t"] >= MOVE_MIN_S - 1e-6


def _p2(k) -> np.ndarray:
    return np.asarray(k["pos"][:2], float)


def _step_ok(P, S, i: int, fps: int) -> bool:
    """Frame i to i + 1 is part of a walk or a run: no move, or a move inside segments that are walks (no jump
    between them). Two keys at one time with different places are a jump with no segment between them."""
    if float(np.hypot(*(P[i + 1] - P[i]))) < 1e-3:
        return True
    a, b = S[i], S[i + 1]
    if a is not None and b is not None and a[0] is b[0] and a[1] is b[1]:
        return _move_ok(a)
    # different segments (or a hold): where one ends the next has to start
    end = _p2(a[1]) if a is not None else P[i]
    start = _p2(b[0]) if b is not None else P[i + 1]
    if float(np.hypot(*(start - end))) > 0.01:
        return False
    return all(_move_ok(x) for x in (a, b) if x is not None)


def _allowed(allow, shot: str, who: tuple[str, ...], cast) -> bool:
    for a in allow or []:
        sh, _, rest = a.partition("/")
        if sh != shot:
            continue
        if not rest:
            return True
        names = [n for n in rest.split("+") if n]
        if not all(n in cast for n in names):
            return True   # a note ("S12/hug"): the whole shot
        if set(names) <= set(who) or (len(names) == 1 and names[0] in who):
            return True
    return False


class Film:
    """Every frame of the edit: each cast member's state, visibility and shot."""

    def __init__(self, st: dict, tl: dict):
        from blocky import acting, checks, polish
        self.st, self.tl = st, tl
        self.fps = tl["fps"]
        self.n = tl["frames"]
        cast = st.get("cast", {})
        self.cast = [k for k, v in cast.items() if not v.get("offscreen") and k in tl.get("acting", {})]
        self.spec = {k: cast[k] for k in self.cast}
        pol = polish.spec(st)
        specs = polish.cam_specs(st, tl, pol)
        self.shot, self.cam = [], []
        self.pos = {w: np.zeros((self.n, 2)) for w in self.cast}
        self.seg = {w: [None] * self.n for w in self.cast}
        self.vis = {w: np.zeros(self.n, bool) for w in self.cast}
        self.yaw = {w: np.zeros(self.n) for w in self.cast}
        self.reach = {w: np.zeros((self.n, 3)) for w in self.cast}   # forward, left side, right side (m)
        for f in range(self.n):
            t = f / self.fps
            sh = _shot(tl, f)
            self.shot.append(sh["id"])
            sp = specs.get(sh["id"])
            cam = None
            if sp and "cam" in sp:
                loc, tgt, lens = checks._cam_at(sp, sh, t, tl)
                cam = (np.asarray(loc, float), np.asarray(tgt, float), lens)
            self.cam.append(cam)
            for w in self.cast:
                s = acting.state(tl, w, t)
                self.pos[w][f] = (s["x"], s["y"])
                self.yaw[w][f] = s["yaw"]
                arm = ARM * float(self.spec[w].get("height", 1.0))
                self.reach[w][f] = (max(0.0, *(math.sin(a) for a in s["arms"])) * arm,
                                    max(0.0, math.sin(s["arms_side"][0])) * arm,
                                    max(0.0, math.sin(s["arms_side"][1])) * arm)
                self.seg[w][f] = acting.position(tl["acting"][w], t, bool((tl.get("motion") or {}).get("ease")))[3]
                if s["hidden"] or cam is None:
                    continue
                self.vis[w][f] = self._seen(cam, s, self.spec[w])

    @staticmethod
    def _seen(cam, s, spec) -> bool:
        loc, tgt, lens = cam
        h = float(spec.get("height", 1.0)) * framing.U
        pts = framing.body_points(s, spec) + [np.array([s["x"], s["y"], s["z"] + framing.HEAD_Z * h])]
        for q in pts:
            p = measure.project(loc, tgt, lens, np.asarray(q, float))
            # in frame, and big enough to see: arm to arm MIN_SIZE of the frame's width or more
            if p is not None and abs(p[0]) <= 1 and abs(p[1]) <= 1 and CLOSE_M * width(spec) * p[2] >= MIN_SIZE:
                return True
        return False

    def foot(self, w: str, f: int) -> np.ndarray:
        """The character's footprint on the ground at frame f: the corners of its shoulders-and-arms box (raised
        arms reach forward, arms out to the side widen it), grown by FOOT_PAD."""
        sp = self.spec[w]
        h = float(sp.get("height", 1.0))
        hw = HALF_W * width(sp) + FOOT_PAD
        hd = HALF_D * h * float(sp.get("width", 1.0)) + FOOT_PAD
        fw, sl, sr = self.reach[w][f]
        y = self.yaw[w][f]
        r = np.array([math.cos(y), math.sin(y)])
        fwd = np.array([math.sin(y), -math.cos(y)])
        c = self.pos[w][f]
        return np.array([c + r * x + fwd * z for x, z in ((-hw - sl, -hd), (hw + sr, -hd), (hw + sr, hd + fw),
                                                          (-hw - sl, hd + fw))])

    def t(self, f: int) -> float:
        return round(f / self.fps, 3)


def lurches(film: Film) -> list[dict]:
    k = max(1, int(round(LURCH_S * film.fps)))
    cuts = {s["f0"] for s in film.tl["shots"][1:]}
    allow = film.st.get("staging_ok", [])
    out = []
    for w in film.cast:
        P, V, S = film.pos[w], film.vis[w], film.seg[w]
        hits = []   # (frame, metres, frames taken)
        step = [_step_ok(P, S, i, film.fps) for i in range(film.n - 1)]
        for f in range(film.n - 1):
            g = min(film.n - 1, f + k)
            c = next((c for c in range(f + 1, g + 1) if c in cuts), None)
            if c is not None:
                g = c - 1   # only the motion inside the shot: the cut itself is checked below
            if g <= f or not V[f]:
                continue
            d = np.hypot(*(P[f + 1:g + 1] - P[f]).T)
            j = int(np.argmax(d))
            # seen where it starts and where it lands: popping in from hidden or from off frame is an entrance
            if d[j] > LURCH_M and V[f + j + 1] and not all(step[f:f + j + 1]):
                hits.append((f, float(d[j]), j + 1))
        # one finding per jump: the biggest window in each run of overlapping hits
        groups = []
        for h in hits:
            if groups and h[0] <= groups[-1][-1][0] + k:
                groups[-1].append(h)
            else:
                groups.append([h])
        for gr in groups:
            a, d, nf = max(gr, key=lambda h: (h[1], -h[2]))
            sh = film.shot[a + nf]
            if _allowed(allow, sh, (w,), film.cast) or _allowed(allow, film.shot[a], (w,), film.cast):
                continue
            out.append({"check": "lurch", "frame": a, "t": film.t(a), "shot": film.shot[a] if film.shot[a] == sh
                        else f"{film.shot[a]}>{sh}", "who": w,
                        "detail": f"moves {d:.2f} m in {nf} frames ({nf / film.fps:.3f} s) from "
                                  f"({P[a][0]:.2f}, {P[a][1]:.2f}) to ({P[a + nf][0]:.2f}, {P[a + nf][1]:.2f}), on camera"})
        # a cut moves anyone anywhere, unless the camera stays put and the character is seen both sides: a jump cut
        for c in sorted(cuts):
            d = float(np.hypot(*(P[c] - P[c - 1])))
            if d <= LURCH_M or not (V[c - 1] and V[c]) or not _same_cam(film.cam[c - 1], film.cam[c]):
                continue
            if _allowed(allow, film.shot[c], (w,), film.cast) or _allowed(allow, film.shot[c - 1], (w,), film.cast):
                continue
            out.append({"check": "lurch", "frame": c, "t": film.t(c), "shot": f"{film.shot[c - 1]}>{film.shot[c]}",
                        "who": w, "detail": f"jumps {d:.2f} m on the cut, seen both sides by about the same camera "
                                            f"(a jump cut)"})
    return out


def _same_cam(a, b) -> bool:
    if a is None or b is None:
        return False
    return (float(np.linalg.norm(a[0] - b[0])) < SAME_CAM_M and float(np.linalg.norm(a[1] - b[1])) < SAME_CAM_M
            and abs(a[2] - b[2]) / max(a[2], b[2]) < 0.15)


def closes(film: Film) -> list[dict]:
    allow = film.st.get("staging_ok", [])
    out = []
    cast = film.cast
    for i, a in enumerate(cast):
        for b in cast[i + 1:]:
            lim = CLOSE_M * (width(film.spec[a]) + width(film.spec[b])) / 2
            both = film.vis[a] & film.vis[b]
            d = np.hypot(*(film.pos[a] - film.pos[b]).T)
            near = both & (d < lim)
            bad = np.zeros(film.n, bool)
            for f in np.nonzero(near)[0]:
                bad[f] = _touch(film.foot(a, f), film.foot(b, f))
            f = 0
            while f < film.n:
                if not bad[f]:
                    f += 1
                    continue
                sh, g = film.shot[f], f
                while g + 1 < film.n and bad[g + 1] and film.shot[g + 1] == sh:
                    g += 1
                m = f + int(np.argmin(d[f:g + 1]))
                lay = _layout(film.pos[a][m], film.yaw[a][m], film.pos[b][m], film.yaw[b][m])
                if not _allowed(allow, sh, (a, b), cast):
                    out.append({"check": "close", "frame": m, "t": film.t(m), "shot": sh, "who": f"{a}+{b}",
                                "detail": f"{d[m]:.2f} m apart (under {lim:.2f}), {lay}, for {g - f + 1} frames, "
                                          f"{film.t(f):.2f}-{film.t(g):.2f} s"})
                f = g + 1
    return out


def _touch(p: np.ndarray, q: np.ndarray) -> bool:
    """Two convex footprints overlap (separating axis test on their edges)."""
    for poly in (p, q):
        for i in range(len(poly)):
            e = poly[(i + 1) % len(poly)] - poly[i]
            ax = np.array([-e[1], e[0]])
            a, b = p @ ax, q @ ax
            if a.max() <= b.min() or b.max() <= a.min():
                return False
    return True


def _layout(pa, ya, pb, yb) -> str:
    """How the two stand, for the reader: side by side (arms into arms), face to face, or one behind the other."""
    v = np.asarray(pb, float) - np.asarray(pa, float)
    n = float(np.linalg.norm(v))
    if n < 1e-6:
        return "one inside the other"
    v /= n
    side = [abs(math.cos(y) * v[0] + math.sin(y) * v[1]) for y in (ya, yb)]   # along each one's shoulders
    if min(side) > 0.7:
        return "side by side"
    if max(side) < 0.5:
        fa = math.sin(ya) * v[0] - math.cos(ya) * v[1]
        fb = -(math.sin(yb) * v[0] - math.cos(yb) * v[1])
        return "face to face" if fa > 0.5 and fb > 0.5 else "one behind the other"
    return "at an angle"


def _wrap(d):
    return (np.asarray(d, float) + math.pi) % (2 * math.pi) - math.pi


def yaws(film: Film) -> list[dict]:
    """A body turning more than YAW_DEG within YAW_F frames, inside one shot and on camera at both ends."""
    allow = film.st.get("staging_ok", [])
    lim = math.radians(YAW_DEG)
    out = []
    for w in film.cast:
        Y, V = film.yaw[w], film.vis[w]
        step = _wrap(np.diff(Y))   # each frame's turn, the short way round
        hits = []   # (frame, radians, frames taken)
        for f in range(film.n - 1):
            if not V[f]:
                continue
            best = None
            for j in range(1, YAW_F + 1):
                g = f + j
                if g >= film.n or film.shot[g] != film.shot[f]:
                    break
                d = abs(float(step[f:g].sum()))
                if d > lim and V[g] and (best is None or d > best[1]):
                    best = (f, d, j)
            if best:
                hits.append(best)
        groups = []
        for h in hits:
            if groups and h[0] <= groups[-1][-1][0] + YAW_F:
                groups[-1].append(h)
            else:
                groups.append([h])
        for gr in groups:
            a, d, nf = max(gr, key=lambda h: (h[1], -h[2]))
            sh = film.shot[a]
            if _allowed(allow, sh, (w,), film.cast):
                continue
            out.append({"check": "yaw", "frame": a, "t": film.t(a), "shot": sh, "who": w,
                        "detail": f"turns {math.degrees(d):.0f} deg in {nf} frame{'s' if nf > 1 else ''} "
                                  f"({math.degrees(Y[a]):.0f} to {math.degrees(Y[a + nf]):.0f} deg), on camera"})
    return out


def lint(st: dict, tl: dict) -> list[dict]:
    film = Film(st, tl)
    rows = lurches(film) + closes(film) + yaws(film)
    rows.sort(key=lambda r: (r["frame"], r["check"]))
    return rows


def table(rows: list[dict]) -> str:
    out = ["| frame | time | shot | check | who | detail |", "|---|---|---|---|---|---|"]
    out += [f"| {r['frame']} | {r['t']:.2f} | {r['shot']} | {r['check']} | {r['who']} | {r['detail']} |" for r in rows]
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--story", type=Path, required=True)
    ap.add_argument("--timeline", type=Path)
    ap.add_argument("--json", type=Path)
    a = ap.parse_args(argv)
    st, tl = measure.load_timeline(a.story, a.timeline)
    if tl is None:
        print(f"{a.story}: no voice-timings.json and no --timeline: nothing to check")
        return 0
    rows = lint(st, tl)
    print(f"# staging: {st.get('name', a.story.name)}: {len(tl['shots'])} shots, {len(rows)} findings")
    if rows:
        print(table(rows))
    if a.json:
        a.json.write_text(json.dumps({"story": st.get("name"), "findings": rows}, indent=1))
    return 1 if rows else 0


if __name__ == "__main__":
    sys.exit(main())
