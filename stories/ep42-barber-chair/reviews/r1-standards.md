# ep42-barber-chair, round 1, standards

Verdict: revise

Fiction, kids and mature themes, IP, originality and package all pass. No lettering in the set, an all-adult cast, nobody hurt, no game name, and the package says "It's made up." The Keeper "gone once the place is filled" shape is shared with ep23 by design (ideas.md batch 4), and the twist itself (my note was in the chair) is its own.

Must-fix (flashing; preview PASS, but the 3-frame reading is 3 at 47.0 s, right at the bar, and the final is measured every frame):

1. S38 (L31, 65.5 s), S45 (L37/L38, 76.9 s) and S66 (L53, 106.5 s) render fully black (preview mean luma 0 to 10) and hard-cut against shots at about 90 to 130. Keep the back sink lamp lit as the flash plan says, and give each one a cool side key so it sits within about 60 luma of its neighbours. S66 has to show the folded cape anyway.
2. S30 (L25, 51.3 s): the flashback grade clips to near-white (mean 248) between shots at 164 and 130. Drop `shot_grades.S30` exposure to 1.0 and bloom to 0.3, or keep S30 in the evening grade as the script plans (S30 is "back to the evening"). Check that S29 doesn't clip either.
3. S53 (L46, 90.7 s): a 1 s white bloom (46, then 192, then 108) is a full-frame dark-bright-dark pulse inside one second. Frame the ring away from the lamp, or cut the bloom so the shot sits near 110.
4. Rerun `python -m blocky flash` and confirm the 3-frame maximum is 2 or lower before the final.

Nice-to-have: pull the 116 to 122 s ring-over-lamp close-ups (about 200 luma) down a little.
