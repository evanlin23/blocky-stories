# Playbook: what to do, ranked by evidence (living file)

Update this every Monday after `metrics.yml` runs: re-rank, move items between confidence levels, retire what the
numbers kill. Each item names its evidence. The sources are `2026-11-03-market-analysis.md` (212 Shorts, 139
channels, 794 comments), `2026-11-03-our-retention.md` (back-row's curve) and the earlier studies in this folder.
Confidence: **high** is a big gap on a decent sample that agrees with earlier research. **Medium** is a clear gap on a
small or biased sample. **Low** is a lead to test, not to rely on.

Last updated 2026-11-03 (first edition).

## The opening recipe (v1, 2026-11-03): the critical path
**The question:** why did 82.6% choose to view back-row, but only 61 to 65% our next three (ep20 64.7%, ep38 61.3%,
knock-back 63.1%; `metrics/studio/2026-11-02.md`)? The feed tests each Short for one to four hours and drops it at
that swipe rate, so this one number decides everything after it.

**What back-row's first 3 s did that the other three didn't** (from each story's `timeline.json` and `story.json`):

| | back-row (82.6%) | ep38 (61.3%) | knock-back (63.1%) | ep20 (64.7%) |
|---|---|---|---|---|
| Line 1 | "On the night bus, you never sit in the back row." **A warning to you**, 11 words, 1.8 s | "In this town, a little silhouette over your head shows who you miss most." A wonder rule, 14 words, 2.5 s | "At my uncle's farmhouse, when the floor knocks, you knock back." An instruction, 11 words, 2.3 s | "It's getting closer." A threat with no subject, 1.0 s |
| Line 2 | "Even if it's the only seat left." Tightens the same warning | Describes the marker | Pause, then "Same rhythm. Every time." | Names a sister and a place |
| Frame 1 | Looks down the aisle **at the forbidden row**, with the figure already sitting in it under a flickering light, pushing in | A mid shot. At 1.3 s it cuts to a wide from 40 m away | A 17 mm low close-up of the floor | A close-up of the photo strip |
| Sound | A drop on "back row" (1.7 s) | none in the first 3 s | knocks from below (1.5 s) | none |
| A name or backstory before 4 s | no | "Dev's stag night" (4.6 s) | uncle | "my sister Wren", "our cousin's wedding" |
| Title | "The driver on my night bus counted 6. I counted 5." A count that doesn't add up | the premise | the premise | a family setup |

**The market agrees:** among story-length Shorts (90 s and up) in the 2026-11-03 scan, **7 of the fastest 17 (41%)
have a warning or danger title** ("Never Be Caught Awake At Night", "Never Ask The Visitor For His Name", "...is
dangerous", "you can't move"), against **3 of the other 71 (4%)**. Confidence in the recipe: **medium-low.** It rests
on four of our Shorts and one scan, and back-row also differs in ways we can't separate (the night-bus setting, the
creature). It's the best-supported bet we have, and the next three films test it.

**The recipe** (every new story, and every queued story before it uploads):
1. **Line 1 is a warning to "you"** about one concrete, everyday thing: "you never...", "never...", "don't...",
   "...is dangerous". At most 12 words and 2.2 s. It isn't a description of how the world works ("In this town,
   X happens"), a feeling, or a whisper with no subject.
2. **Frame 1 looks straight at the thing the warning names, and it's already slightly wrong** (the figure already in
   the back row). Lit to read on a phone and centred for TV (58.5% of back-row's watch time). Push in during line 1.
   No wide or establishing shot in the first 3 s.
3. **A sound hit on the warning's last word.**
4. **Line 2 tightens the same warning** in at most 1.5 s ("Even if it's the only seat left."). No names, places or
   backstory before 4 s.
5. **Lines 3 to 5 show the rule at work,** one shot each, none over 2 s (item 1 below).
6. **The title is the warning or a concrete thing that doesn't add up,** at most 8 words, never the premise phrase.
7. **Measure:** chose to view (Studio) on the next 3 films. **Pass at 75% or more** each. If 2 of 3 land under 70%,
   the recipe is wrong: go back to the table above and test the setting or the creature instead.

The queue, scored against this, is in `docs/research/queue-audit.md`.

## Do (ranked)
| # | Do this | Evidence | Confidence |
|---|---|---|---|
| 1 | **Put the rule in the first line, and show it at work by line 3.** No routine or who's-who lines before the first example. | back-row lost 55 points in 0 to 8 s (loops plus swipes), most of it on L03 to L05 (routine, describing the driver). The hits' 3 to 5 example montage in the first 15 s (27 hits, `2026-11-01` and `2026-11-02` studies). Studio flagged back-row's rule intro as a "key moment". | medium-high |
| 2 | **Story Shorts run 100 to 150 s. Gags and POV run 20 to 45 s. Skip 46 to 75 s.** | Top 10% median 140 s (middle half 100 to 155). 0 of 28 Shorts at 46 to 75 s made the top 10%. 151 to 180 s has the best median (419K/day, n=20). back-row: 138 s, 84% viewed. Against it: one 24-day-old channel wins at 50 to 57 s (skylox study). | medium-high |
| 3 | **Seconds 15 to 30 escalate or show. Nobody explains the rule there, and no shot holds over 2 s.** | back-row's weakest stretch against similar Shorts (0.72) is an elder explaining over a 3.6 s shot (L12 to L15). Same finding in the 2026-11-02 channel analysis. | medium |
| 4 | **Write one quotable line per story:** an odd or funny rule detail said flatly, short enough to type. Mark it in `script.md`. | 25% of top comments on the 40 fastest quote a line back (34 of 40 videos). Laughs are 24%. "Scared" is 1%. | medium-high |
| 5 | **Titles: about 5 words, one emoji at the end, no hashtags, no question, no number.** | Top 10%: median 5 words (the rest 7), 67% emoji (44%), 29% hashtags (63 to 65%), 0 questions, 10% numbers (33% in the bottom half). Holds inside the story-length group too. | medium |
| 6 | **A relatable family or friend fight under the rule.** | Family words in the top comments of 26 of 40 fast Shorts. The skylox study's fastest is a Mum and screen-time fight. back-row (no family) is our only hit, so it's not required. | medium |
| 7 | **Keep the loop ending.** | back-row's last 6 s are its best part against similar Shorts (0.88 to 0.91), and the 166% at second 0 is loops. The skylox top Short loops. | medium |
| 8 | **Keep 4 PM Central and one a day.** | No publish block wins (top-10% Shorts spread across all six 4-hour blocks; per-hour n is 1 to 15). Young winners post one to two a day. | low (no reason to change) |
| 9 | **A premise that makes the viewer type something specific** (their name, their pick, one word) is the one proven comment engine. | One Short at 0.74% comments per view (median 0.01%), where viewers type their own names. The skylox "Comment WORD" Short (15.5K comments). | low to medium |
| 10 | **Vary the title's shape story to story, and write titles and lines in US English** (Mom, neighbor, cart, gas station). | A blind panel put the 10 real fast-risers' titles at ranks 1 to 6, 10 and 14 against our 30, and named ours as one writer's template (`stories/premise-bank.md`). 62% of our views are US, and the panel marked British words as costing hook strength. | medium |
| 11 | **Use the blackout reveal once, not six times.** Keep the climax lit, or cut to a lit reaction. | back-row's climax (six lights-out beats in 25 s) slid from 0.82 to 0.74 against similar Shorts. | low |

## Don't
| Don't | Evidence | Confidence |
|---|---|---|
| Spend time on descriptions or tags | 20 of 40 fastest have an empty or hashtag-only description. 19 of 40 have no tags. | high |
| Read the format momentum table as weekly | The scans so far are one day apart. "Sad -14%" was a one-day move in a ten-video median. Wait for 4 weekly scans. | high |
| Drop a format on momentum alone | Within-scan checks don't agree with the momentum table (sad's young Shorts run 4.3x its older ones, n=12). | medium |
| Lean on "one word in CAPS" | The top 10% uses caps less (19%) than the median band (26%). | low |
| Copy a hit's premise, even as an example | The reset's example rule "lying makes you shorter" is a live PurpleHat title (#31 in the 2026-11-03 deep list). | high |

## Hypotheses for the 2026-11-09 batch (7 stories)
Each is one change, built in enough stories to compare. Judge on day-7 numbers in `metrics/summary.md`, plus
Studio's viewed vs swiped away (paste it into the summary by hand). Seven stories can't prove anything alone: add
them to the next batches' tallies until each arm has at least 6.

**H1. Length: long stories beat 60 to 90 s.** Build 3 stories at 110 to 150 s and 2 at 60 to 90 s, all built from
the same rules (rule first, example by line 3), plus 2 gags at 20 to 45 s.
- Measure: day-7 views and average view duration (seconds) per arm; average % viewed and stayed vs swiped as guards.
- Win: the long arm's median day-7 views are at least 1.5x the 60 to 90 s arm's, without its stayed-to-watch dropping
  more than 5 points. If the 60 to 90 s arm wins, the reset's length rule stands and item 2 drops to low.

**H2. One quotable line raises comments.** Every story in the batch carries one marked quotable line. The comment job
logs our comments weekly.
- Measure: comments per 1,000 views against back-row's 0.31 (7 on 22,291), and the share of our comments that
  quote a line (count by hand; it's a handful).
- Win: median comments per 1,000 views at least 0.6 across the batch, and at least one comment quoting the marked
  line on 3 of 7 stories. If not, item 4 drops to low.

**H3. Short noun titles beat "In This Town" titles.** 4 stories get a 4 to 6 word "The [thing] ..." or plain rule
title with an emoji at the end. 3 get an "In This Town ..." title (no emoji). Spread across lengths so H1 isn't
mixed in: each length arm gets at least one of each.
- Measure: stayed to watch (Studio, the title shows in the feed on long-press and in search) and day-7 views.
- Win: the noun arm's median day-7 views at least 1.3x. Titles weigh less in the Shorts feed than the first second,
  so a null result is likely and fine. It still settles what to stop agonising over.

## Watch (not enough data yet)
- **Our three Nov 2 uploads** (ep38, ep20, knock-back): their curves arrive by 2026-11-09. Predictions are in
  `2026-11-03-our-retention.md` → "For the Nov 2 uploads". If ep20 (no rule in its first line) doesn't drop more
  in its first 8 s than ep38, item 1 drops to medium.
- **Closer-to-Roblox look vs ours** (RULES → the 50/50 test): no numbers yet.
- **Channel age:** 18 of the 40 fastest are from channels under 13 months old, but only 5 come from channels under
  100K subscribers. Check each week whether any channel under 10K appears.
- **The premise bank** (`stories/premise-bank.md`): did the blind panel's top picks do better once made?
