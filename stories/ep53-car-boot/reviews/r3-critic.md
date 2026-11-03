# ep53-car-boot r3 critic (scoped: r2 must-fixes and the S40 to S43 retime)

Verdict: revise

Shot ids have moved down one since r2: old S55 is now S54, old S56 is now S55.

**r2 must-fixes**
1. L01, S01: fixed. The coat is still blue at 1.0 s, slate by 2.0 s and grey-slate at 2.6 s. S02 lands on full orange on "ORANGE." (4.2 s). The change reads by 2 s.
2. L45, S54 (84.6 to 86.2 s): fixed. Framed in front of the bib, the cord knot is centred and the green tarp flaps sit either side. Luma is 34, against S53 at 67 and S55 at 50, so within 40.
3. L46, S55 (86.2 to 88.8 s): fixed. Both stacked eyes and the mouth stroke beside them are in frame. The face is about half the frame width and the eye whites are the brightest thing in it. It now reads as a creature, not a cute face.

**Broken by the retime**
- S42 (67.43 to 69.13 s): the push runs into the chair-arm block. Luma holds about 116 until 68.5 s, falls through 64 to about 29 (limited range, about 14 full range) by 68.8 s, and stays dark for the last 0.35 s on "on the ARM." Then it cuts to S43 at about 112. The strip stays faintly visible, but this is the same dip to black that r2 flagged at S55. The flash measure still passes, with a worst of 2/s at 66.67 s.

**Scores (avg 7.3)**
Hook 7, scare 7, creature 6, twist 8, lore 8, warm turn 8, shot variety 7, faces 7, sound 7, captions 8.

**Panel (changes only)**
- Creepy fan: no longer swipes at 84.6 s. Comment: "the sideways head is cursed"
- Repeat viewer: stays. Comment: "two strokes on the latch"
- Casual: stays. Notices the blink to dark at 68.8 s, but it doesn't make them swipe.
- Slips: none left from r2. L45 and L46 now match the picture.

**Must-fix**
1. L35, S42, 68.5 to 69.13 s: stop the push before it reaches the arm block. Change key 1 from `[-1.1, 0.85, 0.72]`, lens 38, to `[-1.115, 0.80, 0.73]`, lens 38.6, which is about 70% of the old move. Keep the target. Then check that the S42 luma stays within 40 of S43 for the whole shot.
