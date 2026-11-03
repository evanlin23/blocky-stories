# Queue audit against the opening recipe (2026-11-03)

Every story in `queue.txt` (the PR #107 order), scored against the opening recipe in `playbook.md`. Measured from each
story's `timeline.json` and `story.json`. Sunk cost doesn't count: a story ships only if its first second can do what
back-row's did.

**The headline: none of the 16 passes as it stands.** Every one opens on a wonder rule ("In this town, X happens"),
the shape that got 61 to 65% chose-to-view on ep38 and knock-back. None opens on a warning. So every story we keep needs
a new line 1 and line 2, re-voiced, plus a new first shot that looks at the warned-of thing. The voice is our own TTS
and the render runs on Actions, so a redo costs build time, not money. The rest of each story stays.

Lengths aren't recut here. The 2026-11-09 test (playbook H1) needs both arms, and the queue already has them: 69 to
92 s (moving-day, mirror-maze, ep33, floor-thirteen, ep32, ep31) and 132 to 147 s (the rest).

**knock-back is already uploaded** (Nov 2), so take it out of `queue.txt`.

## Scores
Recipe points: 1 warning line · 2 frame 1 on the warned-of thing, no wide in 0 to 3 s · 4 no name or backstory before
4 s · 6 title. "Wide" means a first-3-s shot with the camera over 9 m from its target, or a lens under 20 mm.

| Story | Len | Line 1 now | 1 | 2 | 4 | 6 | Sad family reveal | Call |
|---|---|---|---|---|---|---|---|---|
| closing-time | 135 | "At the aquarium, the night shift waves goodbye to the big tank." (2.4 s) | ✗ | ✗ (24 m wide at 0 s) | ✓ | ✗ | no | **fix first** |
| moving-day | 88 | "In this town, a house grows to fit the tallest one living in it." (2.5 s) | ✗ | ✗ (13 mm at 2.1 s) | ✓ | ✗ | no (creepy came-with) | **fix first** |
| mirror-maze | 77 | "In this town, your reflection stays behind when you walk away." (2.4 s) | ✗ | ✓ | ✓ | ✗ | no (friend) | **fix first** |
| floor-thirteen | 92 | "In this building, everything you forget turns up on floor thirteen." (2.5 s) | ✗ | ✗ (14 to 20 mm) | ✓ | ✗ | yes (Grandad) | **fix** |
| ep49-car-wash | 141 | "In this town, the bell on your collar rings before every mistake." (2.4 s) | ✗ | ✓ | ✓ | ✗ | yes (brother) | **fix** |
| ep47-fitting-room | 132 | "In this town, every lie you tell pins a white tag to your clothes." (2.5 s) | ✗ | ✗ (28 m at 1.3 s) | ✓ | ~ | yes (uncle) | **fix** |
| ep43-reading-room | 136 | "In this town, the number over your head is how many people know your name." (2.8 s, 15 words) | ✗ | ✗ (9.8 m) | ✓ | ✗ | yes (brother) | **fix** → dropped 2026-11-03 (critic r7: nine must-fixes after two rounds; PR #157) |
| ep45-bee-yard | 138 | "In this world, a clock over your head counts down to your next hug." (2.5 s) | ✗ | ✓ | ✓ | ✗ | no (partner, warm) | **fix** |
| ep42-barber-chair | 137 | "In this town, everyone hums one note of their own, all day long." (2.7 s) | ✗ | ✗ (11 m) | ✓ | ✗ | yes (stepdad) | hold |
| ep48-crazy-golf | 141 | "in this town, your shadow stays where you're happiest." (1.9 s) | ✗ | ✗ (12 to 22 m) | ✓ | ✗ | yes (dad) | hold |
| ep55-caravan-park | 135 | "In this town, moss grows on you while you wait for someone." (2.2 s) | ✗ | ✗ (11 m) | ✓ | ✗ | yes (husband) | hold |
| ep33-chairlift | 69 | "In this town, one day at the top of the chairlift costs a year down below." (2.9 s, 16 words) | ✗ | ✗ (34 m) | ✓ | ✗ | yes (Gran) | hold |
| ep36-ice-huts | 143 | "In this town, the little flame over your head always leans toward home." (2.7 s) | ✗ | ✗ (16 m) | ✓ | ✗ | yes (Grandad) | **drop** |
| ep32-sitter | 87 | "In this town, if nobody looks at you, your face fades." (2.2 s) | ✗ | ✓ | ✓ | ✗ | yes (Mum) | **drop** |
| ep31-dawn-flight | 77 | "In this valley, if your family forgets you, your body comes apart, block by block." (3.2 s, 15 words) | ✗ | ✗ (13.8 mm) | ✓ | ✗ | yes (Dad forgetting) | **drop** |

Point 4 passes everywhere because the rule-first rewrite already moved the names out of the opening. Point 3 (the
sound hit) needs a listen, and the builder checks it on each fix.

## Why hold or drop
The reset allows at most one sad family reveal in three. 12 of the 15 still queued are one, so most can't ship soon
anyway.
- **Hold** (fix only after 3 recipe films pass, and space them out): ep42, ep48, ep55, ep33.
- **Drop:** ep36 (the darkest grade in the queue at exposure -0.75, 143 s, and its homecoming twist matches ep43's and
  ep48's, per the queue's own note), ep32 (a third being-forgotten story with floor-thirteen and ep31, and its
  Mum-reveal is the sad shape the reset is moving off), ep31 (a parent with memory loss as the whole story: the
  heaviest theme in the queue, and the most likely to read as a sad family reveal and nothing else). Their builds stay
  in git if the numbers ever turn.

## The fixes: draft lines 1 and 2, first shot and title
Drafts for the writer, to check against each plot. Re-voice lines 1 and 2 only, and keep everything after.

| Story | New line 1 (warning) | New line 2 | First shot | Title |
|---|---|---|---|---|
| closing-time | "On the aquarium night shift, you never skip the wave goodbye." | "Not even when the fish stop swimming." | Close on the big tank's glass, fish hanging face-on to us, the pale shape far back in the blue | Always Wave Goodbye To The Big Tank 🐟 |
| moving-day | "In this town, never let anyone taller than you move in." | "Your house grows to fit them by morning." | A pencil height mark on the doorframe, the ceiling a hand higher above it, pushing up | Never Let Anyone Taller Move In 🏠 |
| mirror-maze | "In this town, never walk away from a mirror without looking back." | "Your reflection stays in the glass." | A maze pane holding a reflection with nobody standing in front of it | Never Walk Away From A Mirror 🪞 |
| floor-thirteen | "In this building, you never ride the elevator to thirteen." | "That's where everything you forget ends up." | Close on the button panel, 13 lit on its own | Never Ride The Elevator To 13 🛗 |
| ep49-car-wash | "In this town, when the bell on your collar rings, you stop." | "It rings right before your mistake." | A collar bell mid-ring, close | When Your Bell Rings, STOP 🔔 |
| ep47-fitting-room | "In this town, never tell a lie." | "Every lie pins a tag to your clothes." | A white tag stabbing onto a sleeve, close | Never Lie In This Town 🏷️ |
| ep43-reading-room | "In this town, never let your number hit zero." | "It's how many people know your name. Mine says one." | The glowing 1 over the narrator's head, close | Never Let Your Number Hit Zero 🔢 |
| ep45-bee-yard | "In this world, don't let your hug clock run out." | "Mine's been blank my whole life." | A dial over a head at 00:00:03, close | Never Let Your Hug Clock Run Out ⏳ |

US English throughout (playbook item 10). **Vary the titles:** 6 of these 8 drafts start with "Never", which repeats one shape (the panel lesson, hard rule 5). The fix sessions rewrite them so no two in a batch start with the same word. Check each new line against hard rule 8 (no dashes, no semicolons).

## Order once fixed
closing-time, moving-day, mirror-maze (the three without a sad family reveal) go first: they're the recipe's test,
so they need to pass the chose-to-view bar (75%) before the rest upload. Then floor-thirteen, ep49, ep45, ep47 and ep43,
never two sad reveals back to back.
