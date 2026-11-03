# Where our viewers leave (2026-11-03)

Sources: `metrics/videos.json` (YouTube Analytics, through 2026-11-03), `uploads.json`, the Studio read in
`2026-11-02-our-channel-numbers.md`, and each story's timeline (`python -m blocky timeline <story>`, which gives
every line's and shot's start time). One retention point is 1% of the video, so 1.38 s on back-row.

## What we have numbers for

| Upload | Up | Length | Views | Avg viewed | Stayed vs swiped | Curve |
|---|---|---|---|---|---|---|
| back-row ("The driver on my night bus counted 6. I counted 5.") | Oct 31 | 138 s | 22,291 (24.9K in Studio) | 83.9% | 82.6% / 17.4% | yes |
| ep38-drive-in ("In This Town You Can SEE Who Everyone Misses") | Nov 2 | 140 s | none yet | | | no |
| ep20-photo-strip ("Mum asked for one photo of us sitting in the middle") | Nov 2 | 136 s | none yet | | | no |
| knock-back ("In This Farmhouse the Floor KNOCKS Back") | Nov 2 (late) | | not matched by metrics.py yet | | | no |
| ep36-ice-huts | Nov 2 | 143 s | private, not counted | | | no |

**Only back-row has a curve.** YouTube Analytics runs 2 to 3 days behind, so the three Nov 2 uploads should have
curves in the next Monday scan (2026-11-09). The reset's "the uploads after back-row flopped" came from Studio
reads, not from this file. Until those curves land, everything below rests on **one video**: treat it as leads,
not findings. knock-back is missing from `videos.json` entirely: `metrics.py` matches by title and may not have
seen it yet (it went public at 10:04 PM Central on Nov 2). Check on Monday; if it's still missing, the title match
needs a fix.

## back-row, second by second

The curve starts at 166% (loops and replays pile up at second 0) and settles to 100% at about 14 s. Everything
over 100% is replays, so the drops before 14 s mix swipe-aways with loop viewers leaving. The **relative**
column is YouTube's "vs similar Shorts" score (0.5 is typical; higher is better).

| Window | Still watching | Change | Relative | Lines | What's on screen and said |
|---|---|---|---|---|---|
| 0 to 8 s | 166% → 111% | -55 | 0.75 to 0.79 | L01 to L05 | The rule ("On the night bus, you never sit in the back row"), "even if it's the only seat left", then the narrator's routine and the driver ("Same driver. Big guy, knit cap. He never said hello."). Shots S01 to S05, 1.5 to 2.9 s each. Biggest single drops at 2.8 s (-23), 4.1 s (-14), 5.5 s (-7), 6.9 s (-6). |
| 8 to 15 s | 111% → 100% | -11 | 0.73 to 0.75 | L05 to L10 | The counting hook: the driver says a number, "I'd count. Five of us." "Every night he counted one too many." |
| 15 to 22 s | 100% → 94% | -6 | **0.72 to 0.73 (the low)** | L10 to L13 | The flickering back row, then the woman in the green coat explains ("told me not to look at it too long", "She'd ridden this bus for years"). Shot S12 holds 3.6 s, the longest in the first 30 s. |
| 22 to 29 s | 94% → 91% | -3 | 0.73 | L13 to L16 | "The middle seat back there always had a dent in it." Description, no new event. |
| 29 to 70 s | 91% → 83% | -8 over 41 s | 0.75 → **0.83** | L16 to L41 | The nights escalate (driver stands by the door, the night I was the only rider). The flattest stretch, and relative retention climbs. |
| 70 to 98 s | 83% → 75% | -8 | 0.82 → **0.74** | L41 to L58 | The climax: lights blink, its head has turned, lights out, "it was standing", "Out again. It was one row closer", "Its arms were wrong", "Out. Its hands were on the next pole". Six blackouts in about 25 s. |
| 98 to 132 s | 75% → 69% | -6 | 0.77 → 0.87 | L58 to L78 | The turn: the driver says six, it asks for company, it was lonely, "It missed you." |
| 132 to 138 s | 69% → 67% | -2 | **0.88 to 0.91** | L79 to L81 | "These days, I always sit in the back row. The driver says six. And I count six too." Loops into the first line. |

### What it says
1. **The first 8 s is where we lose people**, as on every Short. Our first line is the rule, and Studio's "Key
   moments: Intro, kept viewers watching longer than usual" says it works. The drops at 4 to 7 s are on L03 to L05:
   the narrator's routine and a description of the driver ("Same driver. Big guy, knit cap."). Nothing new happens
   for about 5 s after the rule. **Lead:** the second and third lines should show the rule at work (the count), not
   set up who's who. Confidence: low to medium (one video, but it matches the creepy-lane notes and the hit pattern
   "a 3 to 5 example montage in the first 15 s").
2. **15 to 29 s is our weakest stretch against similar Shorts (0.72).** A knowing elder explains the rule, over the
   longest shot of the opening (3.6 s), then a description. Same finding as `2026-11-02-our-channel-analysis.md`.
   **Lead:** seconds 15 to 30 must escalate or show, never explain, and no shot over 2 s there. Confidence: medium.
3. **The middle (29 to 70 s) was fine.** Relative retention rose from 0.75 to 0.83 while the nights escalated.
   The 138 s length didn't hurt this video: 67% were still there at the end, and 84% average viewed beats every
   benchmark we have. Confidence: medium.
4. **The climax blackouts lost ground (0.82 → 0.74).** Six lights-out beats in 25 s mean several near-black frames
   in a row. On a phone a black frame looks like the video ended, and on a TV (58% of our watch time) it's dull.
   **Lead:** do the reveal-by-blackout once, not six times; keep each step lit, or cut to a lit reaction. Confidence:
   low (one video, and the drop could equally be the long stretch of description lines L52 to L57).
5. **The ending is our strongest part (0.88 to 0.91 relative)** and the loop line works: the curve's 166% at 0 s
   is loops. Keep loop endings. Confidence: medium.

## For the Nov 2 uploads, once curves arrive (what to check)
What's on screen in their first seconds, so Monday's numbers can be read against it:
- **ep38-drive-in:** rule first ("In this town, a little silhouette over your head shows who you miss most."),
  then L02 describes the marker ("A black cut-out, in a thin gold ring.") and L03 to L04 start the example montage.
  Predict: a smaller 4 to 7 s drop than back-row, because the montage starts at L03.
- **ep20-photo-strip:** a whispered line first ("It's getting closer."), no rule, then two lines of who and where.
  Predict: a bigger early drop than back-row (no rule, the setup lines come first).
- **knock-back:** rule-ish first line ("At my uncle's farmhouse, when the floor knocks, you knock back."), then a
  pause beat (P01). Predict: watch for a drop at the pause.
If these predictions miss, the early-seconds lead above is wrong and should be dropped from the playbook.
