# ep58-swing-bridge, round 2, standards

Verdict: revise

All of round 1's fixes are in. The new opening passes fiction, kids, IP and flashing. In S01 (0.0 to 2.2 s) the dull flat hands on the green rail are lit from frame 0, with no fade from black and no text in the set. L01 and L01b have no names or places. ep36's second stool, heater alibi and "Mine glow for…" close are gone, and ep36 is now dropped. Preflight flash on the preview: PASS (1-frame max 1, 3-frame max 2 at 100.4 s, red 0). Narration, title and description have no dashes or semicolons and no banned words. "It's made up." is there. `cover_s` 103.4 falls in S69 (102.47 to 104.37 s) with the face at the sash, and `lane: core` is set.

1. **package.json `pin` (Packaging, the 2026-11-03 reset).** Pins now have to read "Comment WORD if...", and "Whose hands would be glowing right now because of you?" is still the old question form. Change it to: `"Comment GLOW if someone needs you more than they'd ever say."`

Nice-to-have
- **Final flash, watch 96 to 102 s** (S66 to S68). The 3-frame reading peaks at 2 here and runs extended for 0.87 s from 96.27 s. That's the glow ramp on a near full-frame face, with the bar at 3. If the Actions measurement goes over, slow the S68 ramp to 2.5 s or hold S67b's last 0.3 s.
- **Title vs RULES.** "Never Cross This Bridge With DARK Hands 🌉" is an imperative, which RULES → Titles bans. The opening recipe on main (playbook item 6, "the title is the warning") allows it, and it's newer, so I passed it. RULES lines 132 and 163 should be updated to match the recipe.
- **Upload spacing.** ep51 `fossil-hall` and ep41 `orchard-rows` (both about-me, both with a glow marker) share this story's skeleton: a no-glow narrator, an older male relative, and a twist that says my marker was about him. Don't upload them within a few days of this one.
- **US English (RULES → Research).** L02 "CINEMA" could be "MOVIES", and L14 "LODGER" could be "BOARDER". Change these only if they're being re-voiced anyway.
