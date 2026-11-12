# ep102-aunt-peaches, r11 critic: S19 sill camera check (proof run 43312117536, sha e47d28f)

Verdict: revise

Scope: S19 only (L08.2 "on the SILL.", f585-607, 19.5-20.3 s) and whatever the fix touched. Scores carry over from r10. The fix doesn't move them, except that this beat no longer reads.

## Checked
- **Flat frame (decision 11): fixed.** No S19 frame is flat, broken or one colour. The top colour bin is 0.26-0.28 of the frame, std is 64-72, and the white shirt now fills about 35% of the frame, not over 70%. `scripts/frames.py --film` finds nothing in S18-S20. Its one finding, an S02 pop, is outside this fix.
- **S56 unchanged.** The commit only changes the `shot("L08.2", ...)` camera and REV 15 to 16. The S56 camera and acting are untouched.
- **Cut to S20 (car, "But the valley"): clean.** The place, colour and size all change.
- **Sill and peach for the whole shot: NO.** The camera isn't high. It sits at about head height, and his head stands between the lens and the peach. From f585 to f596 (0.4 s, half the shot, right on the punch-word "SILL") the sill is an empty white ledge and no peach shows at all. One peach peeks out at f597, and the row of four only reads from about f601. At 300 px, the first half reads as the back of a head over an empty shelf.
- **Cut from S18: weak.** S18 is also a back view of him at the same sill, from close to the same side and height, so S18 to S19 plays like a jump cut, not a new angle.

## Must-fix
1. **S19 / L08.2, `make_story.py` line 281:** make the camera really high and off his right shoulder, so the eye line to the first peach clears his head from frame 0. For example, start at `[RX + 2.6, RY + 0.6, 3.2]` and end at `[RX + 2.2, RY + 1.0, 3.0]`, aimed at the first peach's spot `[RX + 0.15, RY + 3.2, 1.0]`, lens 22-28. His head should sit at the left edge or under the frame, not over the peach. Check that f585 already shows the single peach (the cue `sill n=1.0` at L08.2-0.1), clear of the head and the caption. Re-proof, then confirm that every S19 frame shows the peach and that the S18 to S19 cut reads as a new angle.
