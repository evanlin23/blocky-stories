# ep132-bus-stop, round 4 critic (narrow render-correctness check)

Verdict: approve

Scope: this only covers the spacing fix in commit 8f1d530 (the qa final fail was arms passing through each other). The story was already approved in r3-critic. Checked in the preview `out/work/ep132-bus-stop/ep132-bus-stop-preview.mp4` (20:26, the build after `out/ep132fix2/B.png`). I pulled frames at about 300 to 360 px wide: 6 fps through S07, 4 fps through S08a-S12, about 3 fps through S20a-S21, plus frames 0-2.

## Scores (changed shots only)
- Bodies separate: 9. No limbs pass through each other in any frame I pulled. The S07 stand-up and arm swing has a clear gap between the woman and the narrator. The driver and narrator in S08a-S10 sit about a shoulder-width apart.
- Faces whole and big enough: 8. S01a narrator about 0.22 of frame width. S08 two-shot about 0.20 to 0.22 each. S21 two-shot about 0.20 to 0.22. The S07 wide is about 0.17 to 0.19 each, the same as the old still f00318, so the fix made nothing worse.
- Captions and rule tag clear of faces: 9. Every caption sits on a torso or the legs. The chalk "41" and its tally read in S01a and the 12.7 s cover frame. "42" and the sun read in S20a-S21.
- Loop frame (frames 0-2): 9. No grey sleeve wedge over the narrator's left arm. The arm is clean blue in all three frames.
- Slimmer cast (body_width 0.6): 8. All six still read as the same people: the woman's sunhat and pink top, the driver's moustache, glasses and grey sweater, the girl's bun and scarf. Nobody looks wrong for it.
- Nothing worse than before: 8. S21 now frames the narrator's whole head. In B.png (the earlier build) it was right at the left edge.

## Panel (spot check)
A phone viewer sees two people side by side at the stop, nothing glitching. There is no new reason to swipe.

## Must-fixes
None.

## Should-fix (not blocking)
1. S08a-S10 (12.03-14.4 s): the driver's left shoulder and arm run off the left edge of the frame. His face is whole, so this is fine. If S08 is re-cut for any other reason, pan the camera about 0.1 m to the left so his whole shoulder is in frame.
