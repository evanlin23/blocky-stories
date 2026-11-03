# ep47-fitting-room: standards, round 2

Verdict: approve

## Round-1 must-fix (originality, batch-1 "pale grey blank-faced creature"): fixed

- `build_empty` in `set.py` no longer has `empty.gape` or the pale grey tube. The head is now a flared stand-up collar in the charcoal pinstripe (`M["pin_collar"]`), open at the top, with a lining inside. The glints sit deep at the back (`y 0.24, z 0.12`) and show only down the collar.
- Frames checked: the Empty sheet (stills from 14:28 to 14:35, after the 14:27 `set.py` change), the preview contact sheet, and preview frames at 66, 88, 95, 98, 104 and 113 s. From the front (S60, S63) it reads as a headless suit with a raised collar and a shirt V. From above and at eye level (S62, S68, cover) it reads as a dark open collar with one or two glints deep down. There's no grey cylinder and no black oval face anywhere. The collar is taller than the 0.35 I asked for, but the problem the fix targeted, a blank grey face, is gone.
- The new cover, `cover_s` 102.4 (frame 3072, "with MINE."), shows the creature clearly lit, with the collar and a glint. Fine.

## Re-checked, all pass

- **Fiction, kids and mature themes, IP:** script changes since round 1 are only L35/S44, L48/S60 and L51 ("It has no TAGS / on it / either. / Just like ME."). Nothing new is real, young-looking or copied.
- **Originality:** nothing else in `stories/` is a headless suit. The lore tie-in doesn't make it match another story.
- **Flashing:** preview PASS. Peaks are 1-frame 1 flash and 3 changes, 3-frame 2 flashes and 4 changes (49.5 s). The loop seam is at most 1 flash a second. The upload's description line will read "0:01 to 2:18". Re-read it on the Actions final.
- **Package:** unchanged apart from `cover_s`. Still lint-clean; preflight shows 0 blocks.

## Nice-to-have

- `tail` is now 0. RULES (Sound) asks for 0.2 to 0.3 s between the last word and the loop cut, so check the final for a clipped "ONE."
