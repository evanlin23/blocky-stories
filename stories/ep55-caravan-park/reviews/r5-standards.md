# ep55-caravan-park: standards, round 5

Verdict: revise

Checked: the r4 must-fix, the diff since r4 (`8df4c3c..7adf56a`), the new preview contact sheet, the S13 stills, preview frames at L10, L17, L20, L56, 72 to 76 s and 103 to 120 s, `preflight` (0 blocks), `notes/cold-viewer.md`.

r4 must-fix 1 (Maggie reads as a woman): **fixed.** With the long white locks, the lashes and the plum skirt she reads as a woman at L10 (S13 stills 18.2 to 19.8 s) and from S20 on. She no longer matches the bench husband. The linked arms at L10 are fine for this check. The cold-viewer run is logged and passes. Fiction, kids, IP, originality and package haven't changed and still pass.

Flashing: pass. The preview reads 2 a second at 74.43 s, 3-frame 2 at 4.37 s, red 0, bar_ep10 pass. 74.4 s (dark grass close-up, then the lit Kneeler, then the fog wide) is still the stretch to watch on Actions.

## Must-fix

1. **The fix hid Maggie's hair flowers. L20 "there are flowers in her hair" now plays over a head with no flowers** (S20 to S22, 35.2 to 36.9 s, preview f01054 to f01114; also none visible at L56, f03159). In `set.py` `build_moss`, the new `jory.lock±1` boxes go from x = R-0.19 to R+0.15 and back to y = -0.35. The six `jory.hairf*` and `jory.hairfc*` discs (x ±0.52 to 0.68, y -0.22 to -0.31) sit inside them, so only a yellow speck shows. Change each flower's `fy` to `-0.40` (the flower-eye `fy - 0.03` then lands at -0.43) so they sit on the front face of the locks. Keep x and z. Then re-render S20 to S22 and the L56 shot. Check in stills that the flowers show on both locks at 36 s and 104.5 s, and re-run flash.

## Nice-to-have

- `stills/sheet.png` only has new S13 frames. The rest are from Nov 2 (pre-recast). Rebuild the full stills sheet so the next round reads the current Maggie everywhere.
