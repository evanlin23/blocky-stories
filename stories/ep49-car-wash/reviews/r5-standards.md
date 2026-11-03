# ep49-car-wash: standards review, round 5 (clarity rebuild)

Verdict: approve

Checked the rebuilt preview (141.4 s, -14.1 LUFS, -1.8 dBTP), `preflight` (flash PASS, 0 blocks), the gate, the diff since r4 (commits 1f1d249 and c5381ed) and frames at 112.0 to 115.0 s, 137.0 to 141.35 s and 98.6 s.

1. **Fiction:** L57, L71 and L72 make no truth claim. The new booth shots (S92, S93) carry no set text. Pass.
2. **Kids and mature themes:** L57 "Every ring in his POCKET was MY mistake" and L72 "And I hear EVERY one" have no death words or peril. The adult narrator is shown `worried` and unhurt. Pass.
3. **IP:** no new face, item or name. Pass.
4. **Originality:** the twist and premise are unchanged. The removed night-bed and empty-booth ending took out the only new-mystery beat. Pass.
5. **Flashing:** pass over the whole film. 1-frame worst is 1 flash/s (14.87 s) and 3 changes/s (122.23 s). 3-frame worst is 2 flashes/s (33.2 s) and 5 changes/s (122.3 s), all under 3/6. Red is 0, the extended run is 0.9 s and bright cuts are at most 2/s. Removing the L71 `tod: night` and `dry` off ramps took away the last light drop. The S93 cut (frame 4196) and the loop seam to S01 (one "up", 0.44) are single steps from steady light.
6. **Package:** lints clean. `shape: stand-in` is sanctioned. `cover_s` 98.6 still lands on the Stutter's face lit from below, caption "SLOWLY,". The description has no dashes, semicolons or banned words. Pass.

## Must-fix

None.

## Nice-to-have

- S93 (139.9 to 141.4 s): the sleeve reaching toward the levers stays hidden behind the panel, so "my hand stops" reads only from the face change. That's for the critic.
- The tail after "one" is 0.4 s (141.0 to 141.4 s), against the 0.2 to 0.3 s in RULES.md.
- 122.3 s (5 changes/s, 3-frame) is the peak. Don't tighten cuts there.
