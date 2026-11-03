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

## v2: the animation itself (2026-11-03, from the craft metrics)

The craft-metrics session (`scripts/measure.py`, `docs/research/craft-metrics.md`) found the engine-level gaps behind
the owner's "make it so the animations feel real and clean and good": every walk started and stopped dead, characters
stood like statues, the camera held still in most shots, and v1's punch-ins ran at 2.1 per 10 s, five times
back-row's 0.44. v2 fixes them in the engine, still only under `look.polish` (`docs/engine.md` → The polish pack).

**The edit's numbers** (`measure.py --story`; ep48 and ep42 measured on copies with `look.polish: true`):

| | ep32 none → v1 → v2 | ep48 none → v2 | ep42 none → v2 | target |
|---|---|---|---|---|
| Camera moving | 0.12 → 0.27 → 0.93 | 0.11 → 0.97 | 0.12 → 0.93 | 0.65+ |
| Punch-ins per 10 s | 0 → 2.07 → 0.69 | 0 → 0.71 | 0 → 0.73 | 0.5 to 0.8 |
| Shots where a character moves | 0.27 → 0.27 → 0.86 | 0.34 → 0.57 | 0.27 → 0.61 | 0.8+ |
| Idle 1 s windows | 0.64 → 0.64 → 0.06 | 0.35 → 0.03 | 0.49 → 0.02 | under 0.10 |
| Walk ends that stop dead | 1.0 → 1.0 → 0.0 | 0.91 → 0.0 | 0.89 → 0.33 | under 0.10 |

- "Shots where a character moves" counts shots with nobody in frame (sets, props, hands) in its denominator, so
  ep48 and ep42 can't reach 0.8. Every shot with a visible character now moves.
- ep42's 0.33 is one acting key out of time order for "me" (`acting.position` reads keys in list order), so he jumps
  at about 61.5 s, 87.9 s and 104 s with or without the pack. It's a story fix, not an engine one.
- `measure.py` now reads walk ends from `acting.position` (so easing counts) and no longer counts a jump to a new
  place behind a cut (a key at the same instant, or over 6 m/s) as a walk. The baselines barely move (ep48 0.95 →
  0.91).

**The film's numbers** (`measure.py <preview>`, ep32 previews: quarter-res, every 4th drawing):

| | none | v1 | v2 |
|---|---|---|---|
| Picture changes per 10 s | 8.2 | 8.4 | 10.4 |
| Longest still | 0.83 s | 0.93 s | 0.47 s |
| Motion energy | 1.56 | 1.59 | 1.94 |
| Brightness, dark frames | 0.31, 6.7% | 0.35, 4.7% | 0.35, 4.6% |
| Flash, loudness, true peak | pass, -14.1, -1.8 | pass, -14.1, -1.7 | pass, -14.1, -1.8 |

The preview's held frames (49%) are the preview's every-4th drawing, not the final's.

**On ones** (the cost of drawing every frame, from run 41564219345's shard times): ep34's 16 shards took 17 to 37
min (491 shard-minutes; the wall time is the slowest shard plus 24 min to finish and mix), floor-thirteen's 12 to 27
min. Our stories draw 50 to 58% of their frames today. Every shot on ones is 1.73 to 1.98 times the drawing (ep34's
slowest shard about 70 min). Only the shots where someone walks, which is where twos read as choppy, is 1.07 to 1.09
times on ep32, ep34 and ep48 (0.92 on floor-thirteen, whose walks are already on ones). v2 does that (`ones: "walk"`).
The camera moves and idle motion are slow enough to stay on twos.

**The critic, round 3** (A none, B v1, C v2, fresh agent): C at least as good as B on every axis: **yes**. Better on
pace and motion: **yes** (5 → 6 → 8). Better on animation quality: **yes** (5 → 5 → 7, "breathing and weight shifts
read as natural"). Overall 6 → 7 → 7.5. No jitter at phone size, and no caption cropped. Its notes:
1. The reveal ("was MUM", 66.5 to 67.5 s): her head tilted while the camera trucked, so her face drifted off centre.
   **Fix:** a shot a reveal lands in is calm: a straight push at half speed and idle motion at a fifth.
2. The push at 68 s was too fast on a short shot. **Fix:** the whole move (push plus arc or truck) is capped at
   0.12 m/s.
3. The hook close-up's push cropped the hair. **Fix:** a camera under 2 m from its target pushes proportionally less.
4. At 26.5 s the push aims at the frame's centre, not the sitter's face. Left for now: aiming at a face needs the
   camera to know who's in frame. Builders can key their own camera on a shot like this, and the pack leaves it alone.
Fixes 1 to 3 are in the engine and tested, not rendered again. The Actions final measures and flash-checks them.

## v2.1: colour, the voice and the cost of ones (2026-11-03, from ep62's final)

The first final with v2, ep62-six-riders (`docs/research/craft-metrics.md`), hit every motion target. It warned on
saturation (0.19), voice over the bed (6.3 dB) and repeated frames (68%).

- **Saturation.** The bright grade's toe added grey to every pixel, and grey washes colour out. It now scales each
  pixel by its luma's lift, so the hue and saturation stay, and the saturation floor goes from 1.06 to 1.1. On
  ep32's drawings (every 40th, grade only): the story's own grade reads saturation 0.565, brightness 0.284 and
  darkest 5% 0.058. v2 read 0.527, 0.322 and about 0.09. v2.1 reads 0.599, 0.329 and 0.097, so it's brighter and
  more colourful than the story's own grade. Part of ep62's 0.19 is the story itself: a pale grey sky and fog
  (`#cfd8de`).
- **The voice.** `measure.py` counts the voice against the music and ambience stems. Mixed here from ep62's own
  narration: no pack 6.1 dB, v2 6.3 dB, v2.1 11.3 dB. ep62's own music (-22.6 LUFS) was the cause, not the pack.
  v2.1 makes the bed quieter (-44 LUFS, and 12 dB lower again under the story's own ambience), ducks the
  ambience, bed and polish sounds 8 dB, and dips the music under the lines by only as much as it takes (0, 2, 4
  or 6 dB) to put the voice 10.5 dB over music and ambience together. ep62 lands at 11.3 dB and ep32 at 14.0
  (no extra music dip needed). Both master at -14.0 LUFS with a true peak of -2.0 dBTP before the encode.
- **Repeated frames.** With the pack, the camera moves in about 95% of the time, and a move drawn on twos judders.
  The only fix is drawing those shots on every frame. `ones: "moving"` does it, with these drawing counts:

  | story | frames | twos (as written) | `walk` (default) | `moving` |
  |---|---|---|---|---|
  | ep62-six-riders (34 s) | 1007 | 510 | 746 (1.46×) | 1007 (1.97×) |
  | ep32-sitter (87 s) | 2603 | 1314 | 1428 (1.09×) | 2603 (1.98×) |
  | ep34-unit-seven (143 s) | 4292 | 2291 | 2515 (1.10×) | 4292 (1.87×) |
  | ep48-crazy-golf (141 s) | 4221 | 2139 | 2322 (1.09×) | 4221 (1.97×) |

  At ep34's measured 12.9 s a drawing on Actions (run 41564219345: 491 shard-minutes for 2291 drawings), `moving`
  takes ep34 to about 920 shard-minutes. That's about 57 min a shard, against 31, so about 30 min more wall time
  per story. The free plan runs 20 jobs at once, and a story is 16 shards, so it nearly doubles how long the
  queue takes to render. ep62-length stories cost little either way. `walk` stays the default until the lead
  decides; set `"ones": "moving"` per story to try it.

**Decision (lead, 2026-11-03): `ones: "moving"` is the default.** The owner's bar is "very high", Actions minutes
are free for this public repo, and about 30 more minutes of render time per story is worth losing the judder now
that the camera moves 96% of the time. `"ones": "walk"` in a story's `look.polish` is the opt-out, for a long,
static story whose render would run over about 2 h. Stories already merged keep their films. Only new merges and
re-renders pick it up. The draw shards' timeout (340 min) has plenty of room.

## v2.2: fewer effects, music under everything (2026-11-03)

The owner, watching the fast-rising Shorts with sound: "It doesnt look like very many sound effects, but we can
probably do them to make it seem higher quality. also there is background music." (RULES.md → Few effects, music
under everything.)

- **Music under the whole film.** `polish.music_spec` makes the story's own score start at 0, and gives any section
  without a sustained voice (drone, pad, choir) a quiet drone and pad, so there's never a stretch of ambience alone.
  The only holes are the `music_drops` before a scare. The voice still sits at least 10.5 dB over the music and
  ambience, measured on the mixes: ep62 10.5 dB, ep32 14.0 dB, both -14.0 LUFS, true peak -2.0 dBTP, energy above
  4 kHz 2.9% and 3.4%.
- **Fewer effects.** No whoosh on plain cuts (only on the punch-ins, about 0.7 per 10 s), one low hit on the hook
  instead of one on every key word, reveal hits kept, and risers at most one per 15 s, the twist's first. Doors
  marked on acting keys stay.

Sound events per 10 s (`measure.py --story`, the builder's own effects and footstep bursts included):

| story | v2.1 | v2.2 | the pack's own share in v2.2 |
|---|---|---|---|
| ep62-six-riders (34 s) | 10.4 | 5.1 | 1.5 |
| dryer-nine (82 s) | 9.7 | 4.6 | 1.1 |
| ep32-sitter (87 s) | 6.8 | 2.5 | 0.8 |

The pack now adds about 1 per 10 s. ep62 and dryer-nine stay over 4 because of their own `sfx` (10 in 34 s and 25 in
82 s: clicks, thuds and whooshes). That's the builder's to trim (`builder.md` → Sound budget), and `measure.py`
now warns outside 2 to 4.

## v2.3: pace (2026-11-03, the craft-metric blocks)

From 6 PM Central today, qa blocks a film under 12.5 picture changes per 10 s (0.5 s steps), 14 at 0.25 s steps,
or motion energy 6.0, or with a 0.25 s run still over 1.0 s (`scripts/measure.py`, PR #163; the hits' medians are
16.5, 21.3, 7.6 and 0.25 s). Every film we had failed them, polished ep62 included (11.3 / 13.4 / 5.7 / 1.33 s).
A slow 0.12 m/s camera move hardly moves the 18×32 grid, so the pace has to come from visible reframing.

v2.3 adds it on the output crop, so it costs no drawing: a steady push through every shot (15%, constant rate, in
then out shot to shot) and an angle cut about every 1.0 s inside shots over 1.6 s (a 1.17× tighter, offset framing
every other part, never in a reveal shot or a quiet span). The total crop is capped at 1.25×. The bright grade's
exposure floor goes to 1.12, and it now keeps every pixel under WCAG's saturated red. The first try failed the
flash bar's red-frame rule: ep32 S09b is 47.7% saturated red, and the tighter crop took it to 53% against the 50%
bar.

ep32's preview (every 4th drawing, so the final reads livelier still), all on the same drawings:

| | no pace (v2.2) | push 0.10, cut 1.1 s at 1.14× | **v2.3: push 0.15, cut 1.0 s at 1.17×** | block |
|---|---|---|---|---|
| Changes per 10 s (0.5 s) | 10.3 | 12.8 | **13.5** | ≥ 12.5 |
| Changes per 10 s (0.25 s) | 11.3 | 14.6 | **15.8** | ≥ 14 |
| Motion energy (0.25 s) | 5.3 | 6.12 | **6.33** | ≥ 6.0 |
| Longest still (0.25 s) | 0.53 s | 0.53 s | **0.53 s** | ≤ 1.0 |
| Brightness | 0.346 | 0.375 | **0.376** | hits 0.45 |
| Saturation | 0.576 | 0.561 | **0.562** | hits 0.51 |
| Flash (house bar) | pass | pass | **pass**, 1 a second at most | pass |

**Critic, round 1 (A no pace, B push 0.15 and cut 1.0 s at 1.17×):** better on pace (6 → 7), but framing (8 → 6),
sharpness (8 → 6) and overall (7 → 6) dropped, so it didn't ship. Its notes, all taken:
1. The side offset pushed faces and the twist's portrait to the edge (47.6, 49.6, 61.3 s). **Fix:** angle cuts are
   centred, with a touch up (dy −0.015).
2. The cuts landed mid-caption and across a walk (4.3 s). **Fix:** each angle cut moves to the nearest caption change
   within 0.35 s, or is dropped, and no part is left under 0.6 s.
3. Two cuts landed in the warm beat (79.7, 80.7 s). **Fix:** no angle cuts in any shot that touches a quiet span.
   ep32's own quiet span should run `["L35", "L38"]` when it comes off hold (its story files aren't changed here).
4. The crop went soft past 1.2×. **Fix:** push 0.12, angle cut 1.12×, the total capped at 1.18×.

**Round 2 numbers** (ep32 preview, same drawings, flash pass at 1 a second at most):

| | no pace | cut every 1.0 s | **v2.3: cut every 0.8 s** | block |
|---|---|---|---|---|
| Changes per 10 s (0.5 s) | 10.3 | 12.5 | **12.7** | ≥ 12.5 |
| Changes per 10 s (0.25 s) | 11.3 | 14.0 | **14.4** | ≥ 14 |
| Motion energy | 5.3 | 6.02 | **6.06** | ≥ 6.0 |
| Longest still | 0.53 s | 0.53 s | **0.53 s** | ≤ 1.0 |
| Brightness | 0.346 | 0.375 | **0.375** | |

The margins are thin on the preview, which draws every 4th frame. The final draws every moving shot on every
frame, so it reads livelier, and qa measures the final.
