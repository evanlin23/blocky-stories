# ep127-thousand-tellings: standards, round 2

Verdict: revise

Checked against the fresh flash film (`picture-flash.mp4`, every frame rendered today). The preview mp4 can't be trusted: 104 of 129 shots mix in stale drawings from the 00:59 render, so S123 cuts back and forth to the old rods by his cheek.

## Fix checklist
1. L57 "Every word of it, / right up to / my CAR.": fixed.
2. L11 "I hadn't fished SINCE." and L13 "So I drove back / that SATURDAY.": fixed.
3. S123 (L66): fixed. The rods lean at frame right, a body-width from his face, with the tips at his chin line.
4. package.json "hold": counted fixed. It must come out before the PR merges, or `upload.py` skips the story.

Regressions cleared: no faces near anything, at most one face per shot, no profile two-shot (S68 to S69 at 35°), and no text in the keys (S119) or window (S116) inserts. Night shots hold steady, apart from the S45 problem below.

## Must-fix (severe)
1. **S45 (L24 "with the lights LOW", 40.73 s, frame 1222):** the lit pool on the gravel snaps on mid-shot. Mean luma jumps from 63 to 92 in one frame, which is a light change in a night-look shot. Have the ground light on and steady from the shot's first frame.
2. **S21 (L10.2 car leaving, 19.43 s, frames 582 to 583):** the follow camera passes through a dark tree trunk, so one frame goes near-black (luma 184, then 82, then 185). This is the film's worst flash spot (3f 3/s at 19.4 s). Move the camera path or the tree so nothing crosses the lens.

## Should-fix (not blocking)
- S114 (L62 "The chalk said", 94.8 s): the tag and slate are blank while 1,000 grows from a dot. Hold 999 until "one THOUSAND".
- `check` warns on L28 "It knew my apartment. My CAR." (the slogan pattern), and the "of it," caption runs under 0.2 s.
- Rebuild the preview from a clean `frames-preview` before the next review.
