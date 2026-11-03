---
role: standards
round: 3
verdict: approve
score: 9/10
---

# ep12-knock-back · Round 3 · Standards and practices

**Standards, 2026-10-31.** I reviewed the round 3 patch on the final render. I didn't change the stage, the story, the render, `qa.json` or any other file. My scratch scripts, outputs and stills are outside the repo, in `/tmp/claude-0/-home-user-content/c2eb1c9d-6fc3-507c-96d9-6463a562d472/scratchpad/stds12r3/`.

**What I reviewed:**
- the final `history-sound/out/ep12-knock-back.mp4`. I hashed it myself: SHA-256 `76b9cdc614a4e4334bd5a7427a42c839645ccef2660b9acd873710c73b5e21d1`, the same as the designer reports. It's 1080x1920, 30 fps, 4409 frames, 146.97 s.
- all 4409 composed frames, built in memory the way `post.encode` builds them (`post.finish(post.drawing_for(...))`, grain seed 0, no rain), from the patched frame store
- `timeline.json` (round 3, with the engine fix `ffb8fa4`), `story.json`, `designer-notes.md` round 3, `04-decision-r2.md`, `qa.json` (02:04, newer than the render, 0 blocks and 0 warnings) and the `03-reel.md` header
- full-size composed stills at 0.5, 1.53, 2.2, 34.5, 44.9, 65.7, 96.0, 97.03, 100.53, 102.0, 104.8, 106.6, 106.8, 107.6, 110.0, 112.53, 114.6, 117.2, 118.63, 120.6, 122.0, 124.73, 133.9, 138.17 and 138.3 s. I also compared S63's round 2 and round 3 drawings (f03376) side by side.

**This is a compliance review, not legal advice.** Nothing here needs a lawyer. The two judgement calls from rounds 1 and 2 still stand: where the blocky style ends and copying the game's look begins, and that a TTS narrator in a cartoon needs no AI disclosure.

## Verdict: approve, 9/10

R6, R7 and R8 are closed on my own measurements, not just the designer's report. No licence is uncleared, no policy is broken, and the patch adds no new problem. The film passes the house flash bar in every second, on both the composed frames and the mp4. The flashing-lights span hasn't moved.

I'm holding back one point because two seconds still sit exactly at the flash cap (S28 and S39, unchanged and allowed), and because of the IP advisory on the fully lit heads, which carries over. Neither is a fix on this film.

## Checklist

| # | Item | | Note |
|---|---|---|---|
| 1 | R6, contact (S61, S62, S65 to S68) | ✓ | Section A |
| 2 | R6, the rest of the keeper's beats | ✓ | Section A, re-probed because the keeper cues for L69 to L79 changed |
| 3 | R7, my cue scan | ✓ | Section B: 0 shots |
| 4 | R7, the designer's `cuescan.py` (the 6 extra acting-key shots) | ✓ | Section B: 0 shots |
| 5 | R7, the visible frames (S22, S71, S75, S74) | ✓ | Section B |
| 6 | R8, `house_report`, composed frames | ✓ pass, ⚠ at the cap in 2 s | Section C |
| 7 | R8, `house_report`, mp4 | ✓ pass, identical to the frames | Section C |
| 8 | R8, the replay seam | ✓ | 0 on every reading |
| 9 | R8, `bound.py` | ✓ | No cut flagged (round 2 flagged S71 and S74) |
| 10 | The flashing-lights span | ✓ unchanged | `0:02 to 2:26` |
| 11 | S01 against my rules | ✓ | Section D |
| 12 | S57 and S59 against my rules | ✓, ⚠ advisory | Section D |
| 13 | S63, the visitor and the cover | ✓ | Section D |
| 14 | Note 11 (it doesn't look AI-made) | ✓ | The 2-frame character swap at S75 is gone |
| 15 | Licences, voice, disclosure, audio | ✓ | Unchanged from round 2. The audio is a remux, and loudness is -14.1 LUFS, -1.7 dBTP |
| 16 | Record hygiene (H) | ✓ | `03-reel.md` header (79 shots, 260 captions, round 3), `02b-script.md` (79), `designer-notes.md` R8 table, and `qa.json` newer than the render |
| 17 | Batch items (ep13's last beat, spacing, ep11's line) | ⚠ carried | Not ep12 fixes. See "Carried" |

## A. R6: contact

I used my `probe.py` on the patched scene. It builds the scene like `bl_story.main`, poses everyone with `acting.state` and `set.animate`, and runs a BVH overlap test of every cast mesh against every keeper mesh. Nothing was rendered.

**S61 to S68, 104.7 to 121.1 s in 0.1 s steps (165 times, twice as fine as the decision asked):**
- **No overlapping pair, with Me or with Ray, at any time.**
- S61: the closest moment is 106.6 s, at 16.1 cm (my leg to its foot). Every other S61 time is over 20 cm.
- S62, S65 and S68: nothing within 20 cm at any time.
- S66 and S67 (115.2 to 119.3 s): the nearest point is its knuckle to my leg, at 5.2 cm by this vertex measure, with no overlap. That matches the designer's figure. It's the hand landing "by my BOOT", not on it.
- Ray is never within 20 cm.

**The rest of the keeper's on-screen beats (155 times: 13.75 to 13.95, 47 to 51, 88.5 to 104.7 at 0.2 s, 121.1 to 124.8 at 0.1 s, 138 to 140 s):** nothing within 20 cm, for either cast member. I ran this because the keeper cues for L69 to L79, and the S57, S59 and S69 cameras, all changed.

**On screen:**
- At 106.6 and 106.8 s ("Not ONCE."), its legs pass across the floor with clear boards between them and my boots. My face is out of frame, which is the decision's fallback. The caption and the picture now agree.
- At 117.2 s, its hand meets the board beside my boot.
- At 120.6 s, my fist meets the board, and its arm is nowhere near my chest.

**L69 "It didn't TOUCH me. Not ONCE." is now true of the picture.** R6 is closed.

## B. R7: cut-frame state

**The engine fix (`ffb8fa4`)** snaps any cue, fx or acting key that falls inside a shot's first frame to the cut. Its test is in `reels/blocky/test_blocky.py`.

**The designer's `r3/cuescan.py`** checks for anything landing after the cut but before the shot's second drawing:
- round 3 `timeline.json`: **0 shots**
- round 2 timeline: 24 shots. That's my 18 plus the designer's 6 acting-key shots (S11, S47, S68, S74, S76, S79), so it does find what it claims.

**My own scan (`stds12r3/cuescan_std.py`)** measures against the time each drawing is actually rendered at (`f0/fps`, per `bl_story`). It includes `from` keys, and it checks that every shot's first frame has a drawing of its own:
- round 3: **0 shots** with a cue inside the first drawing, 0 first frames without their own drawing, and 0 starts off the frame.
- round 2 timeline: 25 shots, the designer's 24 plus S26.
- **S26 is information only.** It's Ray's mouth-flap span (`L30.1`). Its `t` snaps to the cut, but its `t0` is 16 ms later, so at worst the flap starts one drawing late. Nothing in the state swaps, so it's not a finding.

**By eye, on composed frames:**
- **S22 at 34.50 s** opens on the lit dawn yard. The black dip is gone.
- **S71 at 124.73 s** opens in the dawn haze. There are no night frames.
- **S75 at 138.17 s** opens on me kneeling at night. Ray isn't there.

**The S75 second at 138.23 s** still counts 2 flashes on the 3-frame reading, under the bar of 3. My `tr.py` trace explains it:
- frame 4144 is the dark S74 (luma 0.03)
- frames 4145 and 4146 are S75's first drawing (0.19)
- from 4147 the frame settles at 0.14 to 0.16

That's one rise on the cut, then a small dip as I lean into the knock. It's the film's own light, not a borrowed state. R7 is closed.

## C. R8: the whole-film flash re-measure

`safety.house_report` with the 78 cuts from `timeline.json`, on both sources. The higher count governs.

| Reading | Composed frames (4409) | Final mp4 (4409) | Bar | Round 2 | |
|---|---|---|---|---|---|
| 1-frame flashes / changes, max per s | 2 / 5 | 2 / 5 | 2 / 5 | 2 / 5 | pass, at the cap |
| 3-frame flashes / changes, max per s | 3 / 6 | 3 / 6 | 3 / 6 | 3 / 6 | pass, at the cap |
| Red, 1-frame and 3-frame | 0 / 0 | 0 / 0 | 1 | 0 / 0 | pass |
| Extended, 1f / 3f | 0.37 s / 1.07 s | 0.37 s / 1.07 s | under 4 s | 0.73 / 1.07 | pass |
| Red frames (full-screen runs) | 0. Max saturated-red share 0.23 | 0. Max share 0.33 | | 0 | pass |
| Very-different cuts, max per s | 2 (27 cuts) | 2 (the same 27) | 3 | 2 (28) | pass |
| IRIS 25% reading (information only) | 2 / 5 | 2 / 5 | | 2 / 5 | |
| Transitions, 1f / 3f | 106 / 341 | 106 / 341 | | 121 / 353 | |
| **House bar** | **pass** | **pass** | | pass | |

Every count is identical between the frames and the mp4, so the encode adds nothing. My numbers match the designer's R8 table exactly.

**The hot seconds:**
- S28 at 44.53 to 45.57 s: 3 flashes and 6 changes on the 3-frame reading. It's at the cap and unchanged, and the patch didn't touch its light, as the decision required.
- S39 at 65.53 to 65.87 s: 2 flashes and 5 changes on the 1-frame reading. At the cap and unchanged.
- S75 at 138.23 s: 2 flashes on the 3-frame reading, under the bar (section B).
- S68's 2-flash second at 119.8 to 120.6 s is gone.

**The seam** (`wrap_report`, the last 30 frames into the first 30): 0 transitions and 0 flashes on every reading. The end card is 0.003 luma and the new S01 opens at 0.014. Round 2 counted one rise here, and now there are none.

**`bound.py` on the mp4:** no cut flagged.

**The span (`span.py`):**
- first transition: frame 80, 2.67 s (S01 into S02)
- last transition: frame 4372, 145.73 s (S79)
- That's the same span as round 2. The new S01 (the 4.5 cm jump and the dust) adds no counted transition before 2.67 s.

**The package line is confirmed:**

> Flashing lights and fast cuts from 0:02 to 2:26.

⚠ **No margin, for the record.** S28 and S39 sit exactly at the cap on both sources. That's a pass under the house bar. If anyone re-cuts, re-grades or re-encodes this film, it gets re-measured before upload. That's why the upload is tied to the SHA-256 below.

## D. The S01, S57, S59 and S63 frames against my rules

- **S01 (0.5, 1.53 and 2.2 s): ✓**
  - The board and the room have no text, numerals, badge or logo.
  - The dust is small dark specks, not a bright particle burst, and it adds no counted transition (section C).
  - The hook doesn't target kids: it's a dark, cool room with no toy-bright colour.
  - It isn't a cover candidate (no keeper).
- **S57 (96.0 and 97.03 s): ✓**
  - "It was built like" now sits below both eyes.
  - The keeper's skin reads ivory to beige under the cool key, not avatar yellow.
  - The mouth slot is still an empty black bar.
- **S59 (100.53 and 102.0 s): ✓, ⚠ advisory**
  - The neck stump enters the top of the head. That's cartoon body horror with no injury: no wound, no gore, nothing open.
  - Both eyes are above "UPSIDE DOWN.".
  - ⚠ **The head fills the frame and is warm-lit, so it reads tan.** That's my standing round 1 and 2 advisory (a fully lit head can pass for a toy figure). It's fine in the film. **It's not a cover frame.**
- **S63 (110.0 and 112.53 s): ✓**
  - Both eyes now sit above "slid AWAY".
  - The visitor on the frosted pane is still a soft, edgeless dark blur, with no hand, head or human outline.
  - Against round 2's drawing, it's the same composition, raised. The IP read and the visitor read are both unchanged, so my round 2 rulings stand.
  - It's still the safest cover: low-key, the keeper guarding the door, the shadow on the glass. **Packager:** crop or frame so the pane with the shadow stays in the cover, so it reads as "something outside, it's guarding", not just a big head.

## Licences, voice and platform (unchanged from round 2, re-confirmed)

- **Licences:** nothing is new to the channel.
  - The voice is Kokoro-82M `am_adam`, Apache 2.0 (I re-opened its licence on 2026-10-29).
  - The font is Schibsted Grotesk, SIL OFL 1.1.
  - There are no datasets, and QA's `license` check says "no external datasets".
- **Disclosure:** none of YouTube's synthetic-media triggers applies. It's an obvious cartoon with invented characters, and no real person is depicted or voiced.
- **Audio:** all synthesized, and `mix` was a remux of round 2's unchanged audio.
- **Length:** 2:27, inside the Shorts cap. There's no TikTok cut.
- **Channel:** @BuhExplains only.

## For the package (packager): the full standards list

**The file to upload**
- `history-sound/out/ep12-knock-back.mp4`, **SHA-256 `76b9cdc614a4e4334bd5a7427a42c839645ccef2660b9acd873710c73b5e21d1`**.
- Re-hash before upload. Any other file, including a re-encode, needs a new flash measure from standards first.

**Upload settings** (set on this upload in @BuhExplains' own Studio, never left to a channel default)
- **Made for kids: No.**
- **AI use (altered or synthetic content): No.**
- **No song added at upload,** and no YouTube hashtags until the first `/retro`.
- **The description opens with:** `Flashing lights and fast cuts from 0:02 to 2:26.`
- Never write "no flashing", "flash-free", "epilepsy safe" or "photosensitive friendly".

**The title**
- It must not be an imperative rule, so the working title "When the floor knocks, knock back" (still in `status.json`) doesn't ship.
- It must not use ep11's shipped two-sentence shape ("The X counted 6. I counted 5.") or anything ep13 uses.
- It stays in-world and reads as a story.

**Words to avoid** (title, description, pinned comment, tags and channel replies)
- "Roblox" or any game or toy brand name, including when replying to "what game is this".
- "true story", "real", "based on real events", "this happened to me".
- "teen", "kid", "kids", "school", any age (no "19" or "nineteen"), or any kid-targeting term.
- Named creatures or film scenes: the Rake, Slender Man, SCP (or any number), "spider walk", or a film's name.
- "home invasion", "break-in", "intruder", "stalker".
- "AI voice", "no AI", "made by hand", "100% original". Don't name Kokoro, and don't present the narrator as the owner.
- Outside the film, never "it never touched me" or "it never touches you". L69 stays in the film, where the picture now agrees with it.
- Nothing that describes Ray by race, or as a "country" or "farmer" type. He is "Uncle Ray".
- No real place, state or region.

**The cover and thumbnail**
- Use a low-key keeper frame:
  - S63 (about 110 to 112.5 s), with the frosted pane and the shadow in frame, or
  - the upside-down eye in the floor gap (S31, S53, S76).
- Never a fully lit or warm-lit keeper head, so not S59, S57 at full light, or S69 lit.
- No cast member shown hurt, grabbed or touched, and never its hand by or on me. Not S61, S66, S67 or S68.
- The visitor stays an edgeless shadow: no human silhouette, hand or face on the glass.
- No grin on Ray, and Ray isn't the scare.
- No game UI, logo or font, and no catalogue avatar.
- It must not target kids: no toy-bright colours, no child characters, and no "for kids" styling.

**Scheduling (producer, `/week`)**
- ep11, ep12 and ep13 never go up on consecutive days on @BuhExplains. Interleave them with non-horror uploads.

**Comments**
- Moderate the "how is he his uncle" replies.
- Don't name the game in replies.

**Process**
- Run every viewer-facing line (title, description, pinned comment) through `python -m studio voice`.
- **Standards signs the package.** Send me the finished package before upload, and I'll check it against this list.

## Carried (not ep12 fixes, so they don't hold this approval)

| Item | Owner | When |
|---|---|---|
| ep13's last beat should be something other than the narrator repeating the ritual (round 2, D) | ep13 scriptwriter, producer | ep13's next round |
| ep13's 12 lag shots: confirm its final started after `ffb8fa4`, or redraw those first drawings | ep13 motion-designer | before ep13's final is reviewed |
| ep11's description opens with its measured flashing-lights line (adopted in `04-decision-r2.md`) | producer, packager. Standards gives the span | before ep11 uploads |
| Week-level spacing of the three horror stories | producer | `/week` and `standards.md` for the week |
