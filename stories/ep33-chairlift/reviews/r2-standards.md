# ep33-chairlift: standards, round 2

Verdict: revise

## Must-fix

1. **Creature skin, `set.py` line 64 (S24 to S29, S34, S36 to S37, S40 to S42, S56 to S61).** `PUTTY = "#64635f"` renders the cube pale grey, and with pin-dot eyes and a hairline mouth it reads as blank-faced (S42, S61). That is the batch-1 "pale grey blank-faced creature" and is close to back-row's grey passenger. Make the skin a warm clay that isn't grey, such as `#9a7f62`, and thicken the mouth stroke so it reads as drawn. Keep r1's small eyes and the low key. Re-render the test still.
2. **L64 (S66, 107.6 s).** "On my / LAST DAWN," opens the closing section the way the batch-1 "Last NIGHT," did. Change it to `On SATURDAY, / the HALVORS / are at / the GATE.` and re-voice that line only.

## Passes

- **Fiction:** I found no text, signs or place names. The boot laces read as a pattern.
- **Kids:** the cast is all adults. The stopped lift is the only peril and nobody is hurt.
- **IP:** the faces are our own and no game is named.
- **Flashing:** the preview passes at 1 flash/s and 3 changes/s, with no runs. The S37 orbit is fixed. The final carries some risk at the loop seam, where S85's white sun cuts to the dark S01 (area 0.85).
- **Package:** the title is a statement of the rule and doesn't spoil the twist. The pin asks the viewer a question. The description says "It's made up.", `made_for_kids` is false, and I found no banned words or dashes.
- **Twist versus ep30 and ep31:** ep33's twist turns on something else. The bet has never been won, and forty years of forfeits is how the Halvors ride free. ep30 turns on the creature being my belayer, and ep31 turns on my lie leaving a corner empty. The creature plays no part in ep33's reveal. Its arc still follows the shared shape (L13 to L14, L53, L70 to L73), but the owner allows similar ending shapes within a batch.

## Nice-to-have

- Cut "ALL of them." from L73, so that "both seats full, Keeper gone" doesn't echo ep31 and ep26 so clearly.
- Once rebased on main, set `look.flash_safe: true`.
