# ep54-dance-hall: standards, round 1

Verdict: revise

Fiction, kids, IP and originality pass. All cast adult, no set text (shop signs blank, record labels plain), glyphs our own, no game name. Twist, creature and warmth differ from every earlier story. `flash_safe: true` is set, and every `hall`, `ros_mark` and `me_mark` cue ramps 0.4 s or more.

## Must-fix
1. **L64 to L65 (124.1 to 126.9 s), hard rule 8 and the batch-1 list.** "A match was never only for LOVE. / It's whoever you FIT with." is a "not just X but Y" / "Not X, it's Y" cadence. Change L64 to `A match` / `can be FAMILY.` and keep L65. Update `twist` in story.json and the script to match.
2. **cover_s 119.4 (S82, L61).** At thumbnail size this crop shows two skin-tone arm ends in a V with no sleeves, and it reads as bare legs. There's no face either. Set `cover_s` to 97.2 (S69, L49 "is level with HERS"), where the Stilted is lit face to face with Ros. Also widen S82 so both sleeves show, like S18 and S87 (rig rule: show the hand at the end of the sleeve).
3. **Flash risk, 2.8 to 4.6 s (S03 to S05, L02).** The preview reads 3 flashes and 6 changes a second (3-frame) at 3.67 s. That is exactly at the house bar, and the full-frame final can tip it over. Merge S04 (0.46 s) into S03 or S05 so no opener shot is under 0.5 s, then re-run `preflight`. Aim for 3-frame readings of 2 flashes and 5 changes or fewer.

## Nice-to-have
- The `whole` cues at L02, L10 and L12 snap off with no `dur`. Each one lands on a cut (2.77, 20.37 and 23.6 s), so nothing shows on screen. Adding `"dur": 0.3` keeps hard rule 7 true if a shot moves later.
- `stills/` and `stills/sheet.png` (08:59) are older than story.json and set.py. Re-run the stills. The stale f02868 is blank white, but the current preview frame is fine.
