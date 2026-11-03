"""Checks on the finished frames and the text, so the reel can't ship a strobe or unreadable type.

Flashes: a simplified version of the WCAG 2.3.1 general-flash and red-flash tests. It isn't a
certified test (the Harding test is what broadcasters use, and it isn't free; EA's IRIS is free and
stronger). Everything is measured at analysis size (LOW), in WCAG relative luminance.

- **A transition.** Per frame pair, the pixels whose relative luminance changes by 0.1 or more of
  full scale, while the darker frame is below 0.8. If the pixels getting brighter, or the pixels
  getting darker, cover AREA of the screen, the frame is a transition.
- **Its direction** comes from one function, `direction`, which `flash_report` and
  `flashcheck.transitions` both call. When both shares pass AREA, the bigger share wins (an exact
  tie counts as darker). It used to be that any frame with enough brightening counted as a
  brightening, even when more of the screen went dark: both red frames ending were scored as
  brightenings, which hid a flash.
- **Flashes.** Inside each 1 s window, consecutive transitions the same way merge into one
  (darker, then darker again is one change). A flash is a pair of opposite transitions. WCAG fails
  more than 3 in any 1 s window. The merge never reaches outside the window, so a change is always
  counted in the second it happened in. r1's count merged across the whole reel and filed each
  merged change at its last frame, which could carry a change out of its second and hide a flash:
  on the 3-frame reading, the down at 8.37 to 8.50 s was filed at 10.73 s, so the microwave cut at
  8.0 s read 2 red flashes where each second holds 3. Counting per window can only raise a count.
  `_events` and `_max_flashes` keep r1's count, for comparison (`global_merge_max`).
- **The red test** does the same with WCAG's red value: on linear RGB, (R - G - B) x 320 where
  R / (R + G + B) >= 0.8, and a change of more than 20.
- **AREA is 10% of the screen. That's the looser reading, not the stricter one.** WCAG's limit is a
  quarter of any 10 degree field. On a phone held at about 30 cm, that quarter is roughly 5 to 6%
  of the screen, so a 10% threshold lets through flashes WCAG would count.

Because of that, the report carries three more readings next to the 1-frame one:
- **The 3-frame reading** (`*_3f`). Changes that build over up to 3 frames count as one transition
  once their total passes 0.1. A pixel counts on frame i if its luminance is 0.1 or more away from
  any of the 3 frames before it (the darker of the two under 0.8), so a ramp of 0.04 a frame counts
  once its third frame lands. Consecutive same-direction frames then merge as above. This is how
  standards measured r1 (4 flashes in the second from 17.93 s), and it reproduces that figure: 4
  in a second on r1's mp4, the first such second starting at 17.13 s.
- **The 5 s reading** (`*_longest_2ps_run_s`). The longest stretch of time in which every 1 s window
  holds 2 or more flashes, from the start of the first such window to the end of the last. This is
  ep10's test, kept for comparison. It's looser than IRIS's configured rule, which `house_report`
  gates instead (W5, below): IRIS fails when the frames whose second holds 4 to 6 changes add up
  to 4 s in any 5 s window, whether or not they're continuous.
- **`*_worst_at_s`** is where the first second holding the most flashes starts.
- **The red test** gets the bigger-share rule too.

The ep10 bar (decision r1, A2) is stricter than WCAG's: at most 2 general flashes in any second at
10%, at most 3 with the 3-frame reading, at most 1 red, and no 5 s run at 2 or more a second.
`pass` below is still WCAG's (3 or fewer); `bar_ep10` reports the stricter one.

**The house bar (standards, ep10 r2, W5), from ep11 on.** `house_report` adds it next to
`flash_report`, which is left exactly as ep10 measured it. On every reading it also counts
**changes** (`*_max_changes_per_s`): the same-direction runs inside each 1 s window, before they're
paired into flashes. On both readings (the frames before encoding and the decoded mp4, the higher
count governing), a reel must keep to all of these:
- at most 2 flashes and 5 changes in any second on the 1-frame reading, at 10% of the screen
- at most 3 flashes and 6 changes on the 3-frame reading (6 is IRIS's `MaxTransitions`)
- at most 1 red flash in any second, on the 1-frame and the 3-frame red readings
- IRIS's extended-flash rule (`*_extended_s`): in any 5 s window, the frames whose 1 s window holds
  4 or more changes add up to under 4 s. IRIS counts 4 to 6; anything over 6 already fails the
  change cap, so counting 4 and up is the same rule, read the safe way
- at most one full-screen red frame (`red_frames`): a run of frames with RED_FRAME_SHARE of the
  screen or more at saturated red. It's held RED_FRAME_HOLD frames or more, and no frame in the
  RED_AFTER_S after it has more than RED_AFTER_SHARE of the screen at saturated red. The exact
  numbers are this file's first reading of standards' A3 line, for standards to confirm
- no more than BRIGHT_CUTS_MAX cuts in any second between shots of very different brightness
  (`bright_cuts`)
- for information, not gated: the 3-frame general reading at IRIS's own 25% of the screen
  (`general_3f_25_*`)

The red margin (`red_margin`) is the largest linear red ratio, R / (R + G + B), in a picture or a
crop of one, with the pixels at or over RED_CLAMP_LINE (0.78, ep10's fix 1). Crops of our own sims
are clamped under it; the report logs the margin so nobody has to trust that they were.

"""

from __future__ import annotations

import numpy as np

FPS = 30   # blocky's frame rate (timeline.FPS)

AREA = 0.10
LOW = (240, 135)   # analysis size (h, w)
DELTA = 0.1        # a change of relative luminance that counts
DARK = 0.8         # the darker frame must be under this
RED_DELTA = 20.0   # a change of WCAG's red value that counts
BUILD = 3          # frames a change may build over, in the 3-frame reading


def _lin(rgb: np.ndarray) -> np.ndarray:
    c = rgb.astype(np.float32) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def frame_stats(rgb_low: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(relative luminance, red-flash value) at analysis size. The red value follows WCAG's
    definition: on linear RGB, (R - G - B) x 320 where R / (R + G + B) >= 0.8, else 0."""
    lin = _lin(rgb_low)
    y = 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]
    s = lin.sum(axis=2)
    sat = (lin[..., 0] / np.maximum(s, 1e-6)) >= 0.8
    red = np.where(sat, np.maximum(0, (lin[..., 0] - lin[..., 1] - lin[..., 2]) * 320), 0.0)
    return y, red


# ----------------------------------------------------------------------------- one frame's direction

def direction(up: float, dn: float, area: float = AREA) -> int:
    """The one rule for a frame's direction: +1 brighter, -1 darker, 0 not a transition.
    When both shares pass `area`, the bigger share wins, and an exact tie counts as darker."""
    if max(up, dn) < area:
        return 0
    return 1 if up > dn else -1


# Motion is not a flash (owner, 2026-11-02, on ep20's photo-wall pan: "we should fix the detector since that seems
# fairly benign"). In a pan across a high-contrast pattern, about as much of each part of the screen brightens as
# darkens on every frame, so the old reading (whichever share is bigger) flipped direction frame to frame and
# counted 11 "flashes" a second while overall brightness barely moved. A flash is the SAME area going brighter then
# darker. So the shares are taken per cell of a GRID x GRID grid, and only each cell's NET change counts: a pan
# cancels inside every cell, while a whole-screen strobe, or two halves flashing in antiphase, doesn't.
GRID = 4


def _coherent(up: np.ndarray, dn: np.ndarray) -> tuple[float, float]:
    """Screen shares of net brightening and net darkening, cell by cell (see GRID above)."""
    cu = cd = 0.0
    for rows_u, rows_d in zip(np.array_split(up, GRID, axis=0), np.array_split(dn, GRID, axis=0)):
        for cu_, cd_ in zip(np.array_split(rows_u, GRID, axis=1), np.array_split(rows_d, GRID, axis=1)):
            w = cu_.size / up.size
            net = float(cu_.mean()) - float(cd_.mean())
            cu += w * max(0.0, net)
            cd += w * max(0.0, -net)
    return cu, cd


def lum_shares(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    """Shares of the screen getting brighter and darker by DELTA or more from luminance a to b, net per cell."""
    d = b - a
    dark = np.minimum(a, b) < DARK
    return _coherent((d >= DELTA) & dark, (d <= -DELTA) & dark)


def red_shares(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    d = b - a
    return float((d > RED_DELTA).mean()), float((d < -RED_DELTA).mean())


def built_shares(lum: list[np.ndarray], i: int, k_max: int = BUILD, delta: float = DELTA,
                 dark_lim: float | None = DARK) -> tuple[float, float]:
    """Shares of the screen that, on frame i, are `delta` or more brighter (or darker) than any of
    the k_max frames before (the 3-frame reading). With k_max = 1 it's the 1-frame reading."""
    cur = lum[i]
    up_any = np.zeros(cur.shape, bool)
    dn_any = np.zeros(cur.shape, bool)
    for k in range(1, min(k_max, i) + 1):
        d = cur - lum[i - k]
        ok = np.ones(cur.shape, bool) if dark_lim is None else np.minimum(cur, lum[i - k]) < dark_lim
        up_any |= (d >= delta) & ok
        dn_any |= (d <= -delta) & ok
    return _coherent(up_any, dn_any)


def transitions(lum: list[np.ndarray], red: list[np.ndarray]) -> dict[str, list[tuple[int, int, float, float]]]:
    """Every counted transition, per reading: (frame, direction, share brighter, share darker).
    These are the lists the flash counts come from, so a table made from them shows what was counted."""
    out = {"general": [], "general_3f": [], "red": [], "red_3f": []}
    last = {k: 0 for k in out}
    for i in range(1, len(lum)):
        for key, (up, dn) in (("general", lum_shares(lum[i - 1], lum[i])),
                              ("general_3f", built_shares(lum, i)),
                              ("red", red_shares(red[i - 1], red[i])),
                              ("red_3f", built_shares(red, i, delta=RED_DELTA + 1e-6, dark_lim=None))):
            d = direction(up, dn)
            if key.startswith("general") and min(up, dn) >= AREA:
                # net brightening in some regions AND net darkening in others, each over AREA: both are flashing
                # (two halves strobing in antiphase), so it's a change against the last direction, never a hold
                d = -last[key] or 1
            if d:
                out[key].append((i, d, round(up, 3), round(dn, 3)))
                last[key] = d
    return out


# ----------------------------------------------------------------------------- counting

def _events(sign_area: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Merge consecutive same-direction transitions (down then down again is one change, not a
    flash). Input: (frame, +1/-1)."""
    out = []
    for f, d in sign_area:
        if out and out[-1][1] == d:
            out[-1] = (f, d)
        else:
            out.append((f, d))
    return out


def _max_flashes(events: list[tuple[int, int]]) -> tuple[int, float]:
    """Most flashes (opposite pairs) in any 1 s window, and when."""
    best, when = 0, 0.0
    frames = [f for f, _ in events]
    for i in range(len(events)):
        j = i
        while j < len(events) and frames[j] - frames[i] < FPS:
            j += 1
        flashes = (j - i) // 2
        if flashes > best:
            best, when = flashes, frames[i] / FPS
    return best, when


def per_frame_flashes(events: list[tuple[int, int]], n_frames: int) -> np.ndarray:
    """Flashes in the 1 s window that starts on each frame, counted from already-merged events
    (r1's count; see `window_flashes` for the one the report uses)."""
    frames = np.array([f for f, _ in events], int)
    out = np.zeros(n_frames, int)
    for f in range(n_frames):
        out[f] = int(((frames >= f) & (frames < f + FPS)).sum()) // 2
    return out


def window_flashes(trans: list[tuple[int, int]], n_frames: int) -> np.ndarray:
    """Flashes in the 1 s window that starts on each frame. Input: every counted transition as
    (frame, +1/-1), in frame order. Only the transitions inside the window are merged and paired,
    so no change is moved out of the second it happened in."""
    frames = np.array([f for f, _ in trans], int)
    dirs = np.array([d for _, d in trans], int)
    out = np.zeros(n_frames, int)
    for f in range(n_frames):
        d = dirs[(frames >= f) & (frames < f + FPS)]
        changes = int((d[1:] != d[:-1]).sum()) + 1 if len(d) else 0
        out[f] = changes // 2
    return out


def longest_run(per_frame: np.ndarray, at_least: int = 2) -> tuple[float, float]:
    """The longest stretch in which every 1 s window holds `at_least` flashes: (seconds, start).
    Windows starting on frames f0..f1 cover f0 to f1 + 1 s, so one such window alone is 1.0 s."""
    best, start, run, run0 = 0, 0, 0, 0
    for f, n in enumerate(per_frame):
        if n >= at_least:
            if run == 0:
                run0 = f
            run += 1
            if run > best:
                best, start = run, run0
        else:
            run = 0
    if best == 0:
        return 0.0, 0.0
    return round((best - 1 + FPS) / FPS, 2), round(start / FPS, 2)


def flash_report(lum: list[np.ndarray], red: list[np.ndarray]) -> dict:
    tr = transitions(lum, red)
    rep = {}
    old = {}
    for key, name in (("general", "general"), ("general_3f", "general_3f"), ("red", "red"), ("red_3f", "red_3f")):
        trans = [(f, d) for f, d, _, _ in tr[key]]
        per = window_flashes(trans, len(lum))
        n = int(per.max()) if len(per) else 0
        run, run_at = longest_run(per)
        rep[f"{name}_max_flashes_per_s"] = n
        rep[f"{name}_worst_at_s"] = round(int(np.argmax(per)) / FPS, 2) if n else 0.0   # the first such second starts here
        rep[f"{name}_longest_2ps_run_s"] = run
        rep[f"{name}_longest_2ps_run_from_s"] = run_at
        rep[f"{name}_transitions"] = len(tr[key])
        old[name] = _max_flashes(_events(trans))[0]
    first = [f for f, *_ in tr["general"]]
    rep["general_span_s"] = [round(first[0] / FPS, 2), round(first[-1] / FPS, 2)] if first else None
    rep["area_threshold"] = AREA
    rep["tie_rule"] = "bigger share (exact tie: darker)"
    rep["count_rule"] = "merged and paired inside each 1 s window"
    rep["global_merge_max"] = old     # r1's count (merged across the reel), for comparison only
    rep["pass"] = rep["general_max_flashes_per_s"] <= 3 and rep["red_max_flashes_per_s"] <= 3
    rep["bar_ep10"] = {
        "general_le_2": rep["general_max_flashes_per_s"] <= 2,
        "general_3f_le_3": rep["general_3f_max_flashes_per_s"] <= 3,
        "red_le_1": rep["red_max_flashes_per_s"] <= 1,
        "no_5s_run_at_2ps": max(rep["general_longest_2ps_run_s"], rep["general_3f_longest_2ps_run_s"],
                                rep["red_longest_2ps_run_s"]) < 5.0,
    }
    rep["bar_ep10"]["pass"] = all(rep["bar_ep10"].values())
    return rep


def worst_shares(lum: list[np.ndarray], red: list[np.ndarray], f0: int, f1: int) -> dict:
    """The biggest red change on frames f0..f1 (a cut from its first frame to the cut away), on the
    1-frame and the 3-frame readings: the frame, which way, and its share in analysis pixels. This
    is the margin under AREA that the flash count alone doesn't show (decision r1 addendum)."""
    n = red[0].size
    out = {}
    for key in ("red", "red_3f"):
        best = (-1.0, f0, 0)
        for i in range(max(1, f0), min(f1, len(red) - 1) + 1):
            up, dn = (red_shares(red[i - 1], red[i]) if key == "red"
                      else built_shares(red, i, delta=RED_DELTA + 1e-6, dark_lim=None))
            sh = max(up, dn)
            if sh > best[0]:
                best = (sh, i, 1 if up > dn else -1)
        out[key] = {"frame": best[1], "dir": "up" if best[2] > 0 else "down", "share": round(best[0], 4),
                    "pixels": int(round(best[0] * n)), "line_pixels": int(np.ceil(AREA * n))}
    return out


def wrap_report(lum: list[np.ndarray], red: list[np.ndarray], tail: int = 30, head: int = 30) -> dict:
    """What a replay shows: the last `tail` frames, then the first `head` again. Lists every counted
    transition in that sequence by its frame in the reel, and the ones that span the seam."""
    n = len(lum)
    idx = list(range(n - tail, n)) + list(range(head))
    tr = transitions([lum[i] for i in idx], [red[i] for i in idx])
    rows = {k: [[idx[f], "up" if d > 0 else "down", up, dn] for f, d, up, dn in v] for k, v in tr.items()}
    rep = flash_report([lum[i] for i in idx], [red[i] for i in idx])
    return {"frames": [n - tail, n - 1, 0, head - 1], "transitions": rows,
            # frames 0-2 are the ones compared across the seam (the 3-frame reading looks back 3)
            "seam_transitions": {k: [r for r in v if r[0] < BUILD] for k, v in rows.items()},
            "max_flashes_per_s": {k: rep[f"{k}_max_flashes_per_s"] for k in rows}}



# ----------------------------------------------------------------------------- the house bar (W5)

AREA_IRIS = 0.25        # IRIS's own area line, for the information-only reading
EXTENDED_MIN = 4        # a frame counts toward the extended-flash rule from this many changes in its second
EXTENDED_WINDOW_S = 5.0
EXTENDED_MAX_S = 4.0    # ... and fails at this much of any 5 s window
RED_FRAME_SHARE = 0.5   # a "full-screen red frame": this share of the screen or more at saturated red
RED_FRAME_HOLD = 7      # frames it's held at least
RED_AFTER_S = 1.0       # after it ends, for this long ...
RED_AFTER_SHARE = 0.01  # ... no frame has more than this share at saturated red
RED_CLAMP_LINE = 0.78   # crops of our own sims stay under this linear red ratio (ep10 fix 1)
BRIGHT_CUT_RATIO = 2.0  # two shots differ "very much" when their (mean luminance + 0.05) differ by 2:1 or more
BRIGHT_CUTS_MAX = 3     # ... and there are at most this many such cuts in any second
# 2026-11-03 (owner: "Sure and yes"): blocks at the published standards, WCAG 2.3.1's 3 flashes a second and IRIS's
# 6 transitions, plus IRIS's extended rule; red stays at 1. The old house extras (2 flashes and 5 changes on the
# 1-frame reading, from ep10) are warnings now (HOUSE_WARN): they counted fast cuts as flicker.
HOUSE_BAR = {"general": (3, None), "general_3f": (3, 6), "red": (1, None), "red_3f": (1, None)}
HOUSE_WARN = {"general": (2, 5)}


def window_changes(trans: list[tuple[int, int]], n_frames: int) -> np.ndarray:
    """Changes in the 1 s window that starts on each frame: the transitions inside the window,
    with consecutive same-direction ones merged (the count `window_flashes` pairs up)."""
    frames = np.array([f for f, _ in trans], int)
    dirs = np.array([d for _, d in trans], int)
    out = np.zeros(n_frames, int)
    for f in range(n_frames):
        d = dirs[(frames >= f) & (frames < f + FPS)]
        out[f] = int((d[1:] != d[:-1]).sum()) + 1 if len(d) else 0
    return out


def extended_flash(changes: np.ndarray, at_least: int = EXTENDED_MIN,
                   window_s: float = EXTENDED_WINDOW_S) -> tuple[float, float]:
    """IRIS's extended-flash reading: the most time, in any `window_s` window, taken by frames
    whose 1 s window holds `at_least` changes or more. (seconds, start of that window)."""
    hot = (np.asarray(changes) >= at_least).astype(int)
    if not hot.any():
        return 0.0, 0.0
    n = int(round(window_s * FPS))
    c = np.concatenate([[0], np.cumsum(hot)])
    sums = c[np.minimum(np.arange(len(hot)) + n, len(hot))] - c[:len(hot)]
    k = int(np.argmax(sums))
    return round(int(sums[k]) / FPS, 2), round(k / FPS, 2)


def red_frames(red: list[np.ndarray]) -> dict:
    """Full-screen red frames: runs of frames with RED_FRAME_SHARE or more of the screen at WCAG
    saturated red. The bar: at most one run, held RED_FRAME_HOLD frames or more, and nothing over
    RED_AFTER_SHARE at saturated red in the RED_AFTER_S after it."""
    share = np.array([float((r > 0).mean()) for r in red])
    hot = share >= RED_FRAME_SHARE
    runs, f = [], 0
    while f < len(hot):
        if hot[f]:
            g = f
            while g < len(hot) and hot[g]:
                g += 1
            after = share[g:g + int(round(RED_AFTER_S * FPS))]
            runs.append({"frames": [f, g - 1], "held": g - f,
                         "after_max_share": round(float(after.max()) if len(after) else 0.0, 4)})
            f = g
        else:
            f += 1
    ok = len(runs) <= 1 and all(r["held"] >= RED_FRAME_HOLD and r["after_max_share"] <= RED_AFTER_SHARE for r in runs)
    return {"runs": runs, "count": len(runs), "max_saturated_red_share": round(float(share.max()) if len(share) else 0.0, 4),
            "ok": ok}


def red_ratio(rgb: np.ndarray) -> np.ndarray:
    """The linear red ratio R / (R + G + B) of each pixel (0 on black)."""
    lin = _lin(rgb)
    s = lin.sum(axis=-1)
    return np.where(s > 0, lin[..., 0] / np.maximum(s, 1e-9), 0.0)


def red_margin(rgb: np.ndarray, line: float = RED_CLAMP_LINE) -> dict:
    """The red margin of a picture or a crop: its largest linear red ratio, how far that is under
    `line`, and how many pixels are at or over it."""
    r = red_ratio(rgb)
    mx = float(r.max()) if r.size else 0.0
    return {"max_red_ratio": round(mx, 4), "margin": round(line - mx, 4), "pixels_at_or_over": int((r >= line).sum()),
            "ok": mx < line}


def bright_cuts(lum: list[np.ndarray], cuts: list[int]) -> dict:
    """Cuts between shots of very different brightness, and the most in any 1 s window. `cuts` are
    the frames a new shot starts on (the edit's own list, or a region's switch frames). A cut counts
    when the mean relative luminance + 0.05 either side differs by BRIGHT_CUT_RATIO or more."""
    hard = []
    for f in sorted(set(cuts)):
        if 0 < f < len(lum):
            a, b = float(lum[f - 1].mean()) + 0.05, float(lum[f].mean()) + 0.05
            if max(a, b) / min(a, b) >= BRIGHT_CUT_RATIO:
                hard.append(f)
    most = max((sum(1 for g in hard if f <= g < f + FPS) for f in hard), default=0)
    return {"cuts": len(set(cuts)), "very_different": hard, "max_per_s": most, "ok": most <= BRIGHT_CUTS_MAX}


def house_report(lum: list[np.ndarray], red: list[np.ndarray], cuts: list[int] | None = None) -> dict:
    """`flash_report`, plus the change counts, the extended-flash reading, the red frames, the
    brightness cuts, the 25% reading and the house bar (W5). `flash_report`'s own keys are
    unchanged, so ep10's figures read the same."""
    rep = flash_report(lum, red)
    tr = transitions(lum, red)
    n = len(lum)
    bar = {}
    for key in ("general", "general_3f", "red", "red_3f"):
        ch = window_changes([(f, d) for f, d, _, _ in tr[key]], n)
        mx = int(ch.max()) if len(ch) else 0
        ext, ext_at = extended_flash(ch)
        rep[f"{key}_max_changes_per_s"] = mx
        rep[f"{key}_changes_worst_at_s"] = round(int(np.argmax(ch)) / FPS, 2) if mx else 0.0
        rep[f"{key}_extended_s"] = ext
        rep[f"{key}_extended_from_s"] = ext_at
        f_cap, c_cap = HOUSE_BAR[key]
        bar[f"{key}_flashes_le_{f_cap}"] = rep[f"{key}_max_flashes_per_s"] <= f_cap
        if c_cap is not None:
            bar[f"{key}_changes_le_{c_cap}"] = mx <= c_cap
        bar[f"{key}_extended_under_4s"] = ext < EXTENDED_MAX_S
    # IRIS's own area, 3-frame build: for information only
    t25 = []
    for i in range(1, n):
        d = direction(*built_shares(lum, i), area=AREA_IRIS)
        if d:
            t25.append((i, d))
    ch25 = window_changes(t25, n)
    rep["general_3f_25_max_flashes_per_s"] = int(window_flashes(t25, n).max()) if n else 0
    rep["general_3f_25_max_changes_per_s"] = int(ch25.max()) if n else 0
    rep["general_3f_25_extended_s"] = extended_flash(ch25)[0]
    rf = red_frames(red)
    rep["red_frames"] = rf
    bar["red_frames_ok"] = rf["ok"]
    if cuts is not None:
        bc = bright_cuts(lum, cuts)
        rep["bright_cuts"] = bc
        bar["bright_cuts_le_3"] = bc["ok"]
    warn = []
    for key, (f_w, c_w) in HOUSE_WARN.items():
        if rep[f"{key}_max_flashes_per_s"] > f_w:
            warn.append(f"{key}: {rep[f'{key}_max_flashes_per_s']} flashes in a second (old house bar {f_w})")
        if rep[f"{key}_max_changes_per_s"] > c_w:
            warn.append(f"{key}: {rep[f'{key}_max_changes_per_s']} changes in a second (old house bar {c_w})")
    rep["house_warnings"] = warn
    bar["pass"] = all(bar.values())
    rep["house_bar"] = bar
    return rep

# ----------------------------------------------------------------------------- text
