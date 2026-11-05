# ep105-backward-neighbor: DROPPED (batch 10, 2026-11-05)

Dropped after the proof qa failed with the review cap spent (2 rounds + the 1 single-fix rescue, RULES audit decision 3).

## Reviews
- Critic r1: revise (faces 5, lore 4). r2: approve, average 7.6, lowest 6.
- Standards r1: revise (confess share, red-plus box glyph). r2: revise (L01 still read as `confess`). r3 (rescue): approve after L01 became "Vern's calendar says / almost eleven thousand days LEFT. / He said goodbye / the day we MET."
- Preflight 0 blocks, flash worst 3/s, measure 0 blocks, gate OPEN, tests pass. Proof run 41943778750 (sha 8ae9ddfe) drew fully.

## Proof qa: FAIL (qa/ep105-backward-neighbor.json)
Open must-fixes:
1. S85, 71.6-73.0 s ("the day after it HAPPENED"): 1.4 s of flat navy. The camera at (61.66, 6.14) sits behind the photo wall (y 3.3) and films its back.
2. S139, 117.4-118.0 s ("to THEM."): 0.6 s of near-black. The camera at (7.28, 7.48) is inside the house/porch geometry, so S60c (Vern hanging the 0 calendar) never shows.
3. cover_s 95.5 is a wide handshake with small faces. Use a lit close-up of old Vern crying with the 10,950 tag (e.g. 0.3 s).
Also weak: S60 (51.1 s) both faces off frame. scripts/framing.py flagged 15 shots: Vern out of frame at L03/L04/L24, heads cut at S58/S60/S63/S139, small faces S74-76 and S111-112, empty S34/S42/S125.

## To revive
These are camera placements in set.py / story.json plus cover_s, no script change. A new batch could pick it up as a fresh build with the fixes above; it would need its own review rounds.
