# ep49-car-wash: standards review, round 7 (new opening, polish on)

Verdict: revise

Checked: the diff since r6 (L01, L02, S01 to S03, L40/L53 "ledge", package), the preview (140.9 s, -14.1 LUFS, -1.8 dBTP), its contact sheet, the stills sheet, `out/first4s.png`, frames from 58.2 to 59.8 s, `preflight` (0 blocks, flash FAIL) and every queued title on this branch and on origin/main.

1. **Fiction:** the new close-ups (S01, S02) show no set text. L01 and L02 make no truth claim. Pass.
2. **Kids and mature themes:** the pie man is an adult, worried but unhurt. "Mess up" and "third pie" are mild. Pass.
3. **IP:** the brass bell and face are ours. No game name in the title, description or pin. Pass.
4. **Originality:** the title "My Collar Bell Has Never RUNG 🔔" is the only queued title that opens on "My". It shares no frame with the "In This Town / Every X / Your X" titles. It is 6 words with one caps word and one emoji, and it doesn't spoil the clapper. The premise and twist are unchanged. Pass.
5. **Flashing:** FAIL, see must-fix 1.
6. **Package:** lints clean. The description has no banned words, dashes or semicolons, and it says "It's made up.". The pin is a "Comment BELL" ask. Keep `hold` until must-fix 1 passes, then remove it in this PR.

## Must-fix

1. **S42 / L32 (58.27 to 59.77 s), cue `car:q2` (`at: L32`, -5.0 to 1.5, `move: 1.8`):** the dark car is still sliding across the booth window when S42 cuts to the grey tunnel (S43). Together they make 7 changes/s at 3-frame (59.53 s, bar 6). Stop the car short of the frame, for example `to: [0, -2.0]`. Or take the `car:q2` cue out of L32 so the shot holds on the booth. Then re-run `preflight` and confirm `general_3f_changes_le_6` is true.

## Nice-to-have

- `old_title` ("In This Town a Bell RINGS...") doesn't match main's last title ("A Bell RINGS Before Every Mistake"). Record the title that main actually used.
