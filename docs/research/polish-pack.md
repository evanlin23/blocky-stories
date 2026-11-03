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
| Flash (house bar, 2603 frames) | pass | pass | ROUND2_FLASH |
| Integrated loudness, file | -14.1 LUFS | -14.1 LUFS | ROUND2_LUFS |
| True peak, file | -1.8 dBTP | -1.8 dBTP | ROUND2_TP |
| Voice over the lines | -13.9 LUFS | -13.9 LUFS | ROUND2_VOICE |
| Quietest 100 ms of the film | -59.0 dBFS | -54.2 dBFS | ROUND2_QUIET |
| Inside the two drops before the scares | -54 dBFS | -50 dBFS (room bed) | ROUND2_HOLE |
| Energy above 4 kHz | 3.3% | 3.4% | ROUND2_HF |
| Still runs over 1.5 s | 0 | 0 | 0 |
| Mean frame brightness at six stills (0 to 255) | 39 to 147 | 49 to 159 | same grade |
| Darkest 5% of pixels at those stills | 0 to 22 | 7 to 32 | same grade |
| Polish events | | 39 whooshes, 7 low hits, 2 risers, 1 reveal hit | ROUND2_EVENTS |

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
- ROUND2_SPECTRO

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

**Round 2:** ROUND2_CRITIC

## What it costs

Nothing new to render: the pack is post and sound only, on the drawings we already make. Finishing the preview
took about 11 minutes and mixing about 6.5, the same as without it.
