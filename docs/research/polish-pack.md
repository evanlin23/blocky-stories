# The polish pack: proof on ep32-sitter (2026-11-03)

Owner, 2026-11-03: "make them high quality or keep pushing the quality up... we can use the new assets or sound
effects, doing rerendering. maybe adding more post sfx or post editing". The pack (`look.polish`, `blocky/polish.py`,
`docs/engine.md` → The polish pack) adds only post and sound, so a before/after can use the same drawings.

**Method.** ep32-sitter: none of the six opening-fix sessions was editing it, and it hadn't been uploaded. One preview
render (quarter-res, every 4th drawing, 86.8 s, 59 shots), finished and mixed twice: A without the pack (as merged), B
with it. Then a blind critic comparison of A and B (the critic agent, told only which axes to judge), one fix round
on the engine, and B again.

## Numbers (A → B)

| | A (before) | B (round 1) | B (round 2) |
|---|---|---|---|
| Flash (house bar, 2603 frames) | pass | pass | pass |
| Integrated loudness, file | -14.1 LUFS | -14.1 LUFS | -14.1 LUFS |
| True peak, file | -1.8 dBTP | -1.8 dBTP | -1.7 dBTP |
| Voice over the lines | -13.9 LUFS | -13.9 LUFS | -13.9 LUFS |
| Quietest 100 ms of the film | -59.0 dBFS | -54.2 dBFS | -54.3 dBFS |
| Inside the two drops before the scares | -54 dBFS | -50 dBFS (room bed) | intact (critic: the silences at 48.3 s and 65.3 s hold in both) |
| Energy above 4 kHz | 3.3% | 3.4% | 3.4% (B minus A above 4 kHz: -56 dBFS over the film) |
| Still runs over 1.5 s | 0 | 0 | 0 |
| Mean frame brightness at six stills (0 to 255) | 39 to 147 | 49 to 159 | same grade |
| Darkest 5% of pixels at those stills | 0 to 22 | 7 to 32 | same grade |
| Polish events | | 39 whooshes, 7 low hits, 2 risers, 1 reveal hit | 37 whooshes (between lines only), 17 low hits on key words, 2 risers of 1.8 s, 1 reveal hit; 19 punch-ins |

## Stills (left A, right B)

The grade is the biggest visible change: the face and the room read on a TV instead of sinking into black, and the
hook's punch-in on "your face FADES." frames the face tighter.

- `polish-pack/still-00.jpg`, 1.6 s (the hook, punch-in on FADES)
- `polish-pack/still-01.jpg`, 27.2 s (the faded sitter)
- `polish-pack/still-02.jpg`, 31.2 s (its face)
- `polish-pack/still-03.jpg`, 50.0 s (the scare: "BESIDE ME.")
- `polish-pack/still-04.jpg`, 64.5 s (through the wet glass)
- `polish-pack/still-05.jpg`, 66.8 s (the reveal, "was MUM.")

## Spectrogram notes

- `polish-pack/spectrogram-before.jpg` and `-after.jpg` (whole film, 0 to 8 kHz) and `scare-before.jpg` and
  `scare-after.jpg` (45 to 52 s, 0 to 6 kHz).
- Round 1: nearly identical. Both drops show as dark columns at about 48 s and 65 s; B's hole sits about 4 dB higher
  (the room bed) instead of near digital silence. The whooshes sat 15 to 20 dB under the mix and didn't show, and the
  riser read only in its last 0.3 s (its curve was squared and it ducked under the voice running into the drop).
- Above 4 kHz stays at or below -42 dBFS everywhere in B (critic): nothing scratchy.
- Round 2: B minus A shows the pack adds sound only below 300 Hz (critic): risers sweep 170 to 300 Hz at 47.0 to
  48.0 s and 63.8 to 65.1 s and stop where the silence starts; their peaks sit about 3 dB under the program, so
  they shouldn't go louder. The hit on "MUM" (66.9 s) is 2 dB under the voice. Whooshes and key-word hits sit 8 to
  15 dB under the voice. No 0.1 s window of what the pack adds goes above -40 dB over 4 kHz.

## The critic's comparison

**Round 1** (A vs B): B at least as good on every axis: yes. Better on sound: yes, a small step. Better on pace: no.
Picture on a TV 6 → 8 ("A crushes blacks: 26% of pixels at or below 16 at 49 s"), hook 7 → 8, effects 6 → 7,
everything else equal. Its notes, all taken into the engine, not just ep32:
1. The reveal hit landed on "was", 0.3 s before "MUM". **Fix:** every hit and punch-in now lands on the chunk's key
   word (estimated from the letters before it, `polish.on_key`).
2. A hit on "And it was sitting", not a key word. **Fix:** the same.
3. A cold hit on the warm "Not BAD". **Fix:** `quiet` refs (no hit there); ep32 marks L36.5 quiet.
4. The last hit on "So why" instead of "SEE". **Fix:** ep32 marks L40.4.
5. The riser was too short to build. **Fix:** its own 1.8 s swell (noise 250 to 2800 Hz plus a rising sine, curve
   ^1.3), on its own bus so the voice doesn't duck it; still cut by the drop.
6. No whooshes heard, and pace unchanged. **Fix:** whooshes up 5 dB (-19), low-passed at 3 kHz, and only on cuts
   between lines (never under a word) and on punch-ins; a fill punch-in in every shot over 2.2 s that has none, and
   the auto marks (all-caps captions, big words, the hook) now add to the builder's own.

**Round 2** (A vs the fixed B, a fresh critic): B at least as good on every axis: **yes**. Better on sound:
**yes** (7 → 8). Better on pace: **yes** (7 → 8; frame-to-frame motion up about 23%, punch-ins land on "FADES" and
"MUM", nothing jarring). Picture 7 → 8 (frames under brightness 40 fall from 5.8% to 2.2%; shadows lifted, not
washed out). Hook and captions equal at 8 (the caption pop doesn't show at the preview's frame rate). "Not BAD" has
no hit. Its notes, taken after round 2 (in the engine and tested, not rendered again; the Actions final mixes and
flash-measures them):
1. A whoosh and a fill punch-in at 77.5 s, inside the warm beat. **Fix:** `quiet` takes a span (`["L35", "L37"]`):
   no whoosh, hit or added punch-in in it, only the drift. ep32 marks its warm turn.
2. The room bed doesn't show above the leftover difference (-36 dB). **Fix:** the bed goes from -44 to -41 LUFS.
3. Don't push the risers louder. Kept.

**Verdict:** the pack goes in, and it's the default for new stories (`builder.md`, `critic.md`, `qa.md`).

## What it costs

Nothing new to render: the pack is post and sound only, on the drawings we already make. Finishing the preview
took about 11 minutes and mixing about 6.5, the same as without it.
