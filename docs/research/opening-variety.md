# Opening variety: one recipe, six shapes (2026-11-03)

**The problem.** The opening recipe (`playbook.md`) asked for "a warning to you" in line 1. The fixes read it as the
word "Never". Of the 29 queued or in-flight stories, about 20 opened with "Never", "Don't" or "you never". Uploaded
back to back, that's the "narrated stories with only superficial differences" pattern that YouTube names first and
that hard rule 5 forbids. (Standards flagged it, 2026-11-03.)

**What the data actually says.** The fast story Shorts open on many shapes, and very few say "Never". These are title
counts over 270 rising story Shorts: the 2026-11-03 blocky scan plus the wide scan's horror, storytime and what-if
rows. The top fifth is the 54 fastest.

| Shape | Example from the scan | All 270 | Top 54 | Median views/day |
|---|---|---|---|---|
| Rule of the place, with its cost ("In this town…", "Everyone gets…", "Nobody…") | "Everyone Gets 100 Jumps..." | 32 | **9** | 183K |
| "The [thing]…" mystery | "The Knocker Copies Your Voice" | 25 | **9** | 74K |
| First person ("I…", "My…") | "I Could CONTROL The Entire Town, Until..." | 9 | 4 | 248K |
| What if | "What if your Ice-cream got Colder every 2 Seconds?" | 16 | 3 | 179K |
| If or when you… | "If You Hear Three Knocks, Don't Open!" | 8 | 3 | 249K |
| You must / you can't | "IN THIS WORLD YOU CAN'T MOVE" | 3 | **3** | 651K |
| **Never / Don't** | "Never Be Caught Awake At Night" | **4** | 1 | 305K |
| A count that doesn't add up | (our own back-row: "The driver… counted 6. I counted 5.", 82.6% viewed) | 5 | 0 | 17K |

So the recipe's point 1 stays: a concrete threat or mystery aimed at you, in at most 12 words and 2.2 s. **"Never"
is one way to say it, and a rare one among hits.**

## The six line-1 shapes (all satisfy the recipe)
Tag each story's `package.json` with `"opening": "<key>"`. `upload.py` won't put two uploads in a row that share an
opening (the same as the twist `shape`).

| Key | Shape | Pattern | Example |
|---|---|---|---|
| `ban` | A ban | "Never X." / "Don't X." | "In this town, never walk away from your reflection." |
| `if` | A condition | "If you X, Y." / "When X, you Y." | "If the thirteen button lights up by itself, don't step out." |
| `must` | An obligation | "Here, you have to X." / "You can't X." | "On the aquarium night shift, you have to wave goodbye to the big tank." |
| `count` | A count that's wrong | "Twelve people. Eleven clocks." | "Four people got in the elevator. The mirror shows five." |
| `confess` | First person, already in it | "I X. Now Y." / "My X…" | "I kept one secret, and now I glow." |
| `cost` | The place's rule, with its price | "Nobody here X." / "An hour up there costs…" | "Nobody at this laundromat uses dryer nine." |
| `whatif` | The what-if lane only | "What if X every N seconds?" | (what-if Shorts) |

**The limits:**
- No two uploads in a row share an opening.
- `ban` is at most 1 in 4 of a week's uploads.
- No other shape is over 1 in 3.
- Line 2 still tightens the same threat.

**Titles:**
- Use the same family of shapes ("The [thing]…" is the second most common among hits).
- At most one "Never" title per 7 (RULES already).
- **CAPS word (a recommendation for the owner, not a rule):** the one-CAPS-word title is the owner's own call
  (2026-11-02), so it stays. For the owner to weigh:
  - Every queued title uses that form, which is a template of its own.
  - In the 2026-11-03 scan, a CAPS word appears in 19% of the top 10% of titles (4 of 21), against 26% of the median
    band (11 of 43). That's neutral to slightly negative, on a small sample.

## Every queued and in-flight story, assigned
Line 1 is as it stands now (`main` or the story's open branch). The **new line 1 and line 2** are drafts for the owning
session: re-voice lines 1 and 2 only and keep everything after them. "keep" means no change.

**The queue, in upload order:**

| # | Story | Line 1 now | Opening | New line 1 | New line 2 | Owner |
|---|---|---|---|---|---|---|
| 1 | closing-time | You never skip waving goodbye to the big tank. | **must** | On the aquarium night shift, you have to wave goodbye to the big tank. | Even if nobody's watching. (keep) | fix A |
| 2 | moving-day | In this town, when your ceiling rises, don't look up. | **if** | If your ceiling is higher this morning, you're not the tallest one living there. | Ours went up a meter last night. | fix A |
| 3 | mirror-maze | In this town, never walk away from your reflection. | **ban** | keep | keep | fix A |
| 4 | floor-thirteen | If the thirteen button lights up by itself, don't step out. | **if** | keep | keep | fix B |
| 5 | ep49-car-wash | When your collar bell rings, stop. You're about to mess up. | **must** | Here, you have to freeze the second your collar bell rings. | It means you're about to mess up. | fix B |
| 6 | ep45-bee-yard | Never let a man with no clock near someone you love. | **count** | Twelve people on the pier. Eleven clocks. | Every clock counts down to your next hug. (keep) | fix B |
| 7 | ep47-fitting-room | Don't lie in this town. Every lie pins a tag on you. | **must** | In this town, you can't hide a lie. It pins a tag on you. | My uncle never lies. He's covered in them. (keep) | fix C |
| 8 | ep43-reading-room | Don't let the number over your head drop to one. | **confess** | My number dropped to one today. | It counts who knows your name. Nobody's is that low. | fix C |
| 9 | ep42-barber-chair | In this town, everyone hums one note of their own, all day long. (old, not recipe-fixed) | **cost** | Everyone here hums a note of their own. Mine went silent. | You can see it. A ring over every head. | **no fix session yet** |
| 10 | ep48-crazy-golf | in this town, your shadow stays where you're happiest. (old) | **count** | Nine holes. Ten shadows on the last green. | Here, your shadow stays where you were happiest. | **no fix session yet** |
| 11 | ep55-caravan-park | Never wait for someone at the front gate. | **ban** | keep | keep | (merged) |
| 12 | ep33-chairlift | Don't sit on the bench at the top of this chairlift. | **cost** | An hour on the top bench costs two weeks down here. | Gran goes up every morning. | fix F |

The queue's sequence: must, if, ban, if, must, count, must, confess, cost, count, ban, cost. No neighbours repeat,
and `ban` is 2 of 12.

**In flight, not yet queued:**

| Story | Line 1 now | Opening | New line 1 | New line 2 | Owner |
|---|---|---|---|---|---|
| ep37-comet-night | Promises tie knots over your head. Don't let one pull tight. | **cost** | keep | keep | fix F |
| ep41-orchard-rows | Every footprint here glows. Don't walk beside one that doesn't. | **count** | Two trails of footprints. Only mine glows. | Here, every footprint glows until sunrise. | fix F |
| ep46-choir-hall | in this world, everyone gets ten words a day. (old) | **confess** | I used all ten of my words before breakfast. | In this world, ten a day is all you get. | fix C |
| ep50-beach-huts | don't let anybody see your reflection in a window. | **if** | if someone sees your reflection in a window, they'll know what you really want. | it does whatever you really want. (keep) | fix D |
| ep51-fossil-hall | in this town, never keep a secret. | **confess** | i kept one secret, and now i glow. | in this town, everybody can see it. | fix D |
| ep52-ferry-crossing | Never drop anything here unless you want it back. | **if** | If you drop something here, it hops home after you. | Even the things you meant to lose. | fix D |
| ep53-car-boot | the scariest coat never changes color. | **cost** | keep | keep | fix E |
| ep26-last-skate | At this rink, slow songs are couples only. Everyone else waits at the rail. (old) | **must** | At this rink, you can't skate a slow song alone. | Nan always waited at the rail. Tonight, something waited with her. | fix E |
| ep54-dance-hall | never cover the back of your hand. your match has the rest. | **cost** | everyone's born with half a mark. someone out there has the rest. | never cover yours. not even in winter. | ep54 session |
| ep58-swing-bridge | If your hands stop glowing, stay off the old bridge. | **if** | keep | keep | (merged) |
| ep28-lamp-room | In this lighthouse, never leave your floor after dark. | **must** | In this lighthouse, after dark you have to stay on your floor. | Not even for a text. (keep) | ep28 session |
| warm-shoes (batch 6 P1) | never keep the shoes our cat brings home, they're still warm. | **confess** | every night our cat brings home shoes. they're always still warm. | never keep them. even if they're your size. | batch 6 |
| ep71-two-windows (P2) | at this drive through, never pull up to the second window. | **count** | this drive-through has one booth and two windows. | never pull up to the second one. | batch 6 |
| night-mower (P3) | Never look at the neighbor's lawn while his mower's running. | **confess** | My neighbor mows his lawn at three a.m. with his eyes shut. | Don't look while it's running. | batch 6 |
| dryer-nine (P4) | At the laundromat, you never use dryer nine. | **cost** | Nobody at this laundromat uses dryer nine. | It runs every night anyway. | batch 6 |
| every-lock (P5) | never let a door shut here. ours has a thousand locks. | **count** | Our bathroom door has one thousand and twenty-four locks. | Every time it shuts, they double. (keep) | batch 6 |
| rule-three (P6) | Never ask who tore out rule three. | **cost** | Rule three is missing, and everyone in town still obeys it. | (the Keeper's line 2, as planned) | batch 6 |
| ep62-six-riders (P7) | four people got in the elevator. the mirror shows five. | **count** | keep | keep | batch 6 |

ep34 is dropped. The older held stories (ep23, ep25, ep30, ep31, ep32, ep36, ep39, ep40, ep44, ep57, lookout) take a
shape when they're fixed. They aren't in the counts.

**All 30 together:**

| Opening | Stories | Share |
|---|---|---|
| ban | 2 | 7% |
| if | 5 | 17% |
| must | 5 | 17% |
| count | 6 | 20% |
| confess | 5 | 17% |
| cost | 7 | 23% |

Before this, about 20 of 29 opened on "Never/Don't".

**Titles to change with the line:**
- **ep54:** "Never Cover the Back of Your HAND" would be the third "Never" title in flight. Make it "Someone Has the
  Other Half of My Mark 🤚".
- **moving-day:** "When Your Ceiling Rises, Don't Look UP" can stay (an `if` title).

Every new line is a draft. The owning session checks it against its own plot, keeps it under 12 words and 2.2 s, and
re-voices lines 1 and 2 only. Qa checks the new first 3 s.

## Update after the sessions replied (2026-11-03, about 11:30 UTC)
The owning sessions checked the drafts against their plots. What they're using:

| Story | Opening | Line 1 as used | Why it changed |
|---|---|---|---|
| closing-time | must | You have to wave goodbye to the big tank. | 9 words, under 2.2 s |
| moving-day | **ban** (kept) | In this town, when your ceiling rises, don't look up. | its gate was already open (orchestrator, today). mirror-maze is also `ban`, so `upload.py` puts floor-thirteen (`if`) between them |
| ep45-bee-yard | count | Two people in the bee yard. Only one clock. | the first shot is the bee yard, not the pier |
| ep47-fitting-room | must | You can't hide a lie here. It pins a tag on you. | 12 words |
| ep43-reading-room | confess | Only one person in this whole town knows my name. (L2: The number over my head says ONE.) | "dropped today" contradicted "has said one for years" |
| ep53-car-boot | cost | The SCARIEST coat never changes COLOR. | unchanged |
| ep54-dance-hall | cost | (as drafted) | L71's loop line echoes the new L1, with "Mine is my AUNT." kept after it |
| ep26-last-skate, ep46-choir-hall | n/a | dropped at triage (PRs #114 and #115) | not the opening |

**Updated counts (28 stories):** ban 3 (moving-day, mirror-maze and ep55: 11%), if 5, must 4, count 6, confess 4,
cost 6. All are within the limits.

The CAPS-title cap was taken out of RULES: that title form is the owner's decision. The numbers are above as a
recommendation for the owner.
