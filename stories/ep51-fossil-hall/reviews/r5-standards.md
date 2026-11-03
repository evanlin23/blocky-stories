# ep51 standards r5

Verdict: approve

Checked against RULES.md as on `origin/main` today (the reset, the title and pin rules, the opening tag in hard rule 5, hard rules 1 to 8).

- **r4 fix 1, US English: done.** L31 "His FLASHLIGHT", L36 "I don't TURN / AROUND.", L72 "Neighbors", and "Grandpa" in every line. The same words are in `story.json`, `generator/lines.json` and the preview timeline captions. The description says "my grandpa" and "Grandpa Abe". "torch" is left only in prop names and shot notes, which nobody sees.
- **r4 fix 2, flashing: done.** `flash` on the preview passes. The 3-frame reading is now 2 flashes and 4 changes a second at most (worst at 18.77 s; r4 was 3 and 6 at 95.87 s). Red is 1, with no extended run. The head roll at 96 s no longer sits on the bar.
- **Opening:** L01 "I kept one secret, and now I glow." and L02 "In this town, everybody can see it." are a `confess` opening, tagged `"opening": "confess"`, the doc's own example. Together they state the rule. No queued story uses `confess`, so it can't repeat back to back. L80 runs straight into L01 as one sentence.
- **Package:** the title "Keep One Secret and You GLOW 💡" has 6 words, one caps word and an end emoji. It's a conditional warning, not a game hint, and has no "Never" and no spoiler. The pin is "Comment GLOW if...", per the reset. `made_for_kids` is false. The description says "It's made up." with no banned words. `cover_s` 97.55 shows the Stooped's face, lit, with "It doesn't GLOW."
- Fiction, kids, IP and originality are unchanged from r3/r4 and pass. `pytest`: 145 passed.

## Nice-to-have
- Keep ep51 away from ep47-fitting-room in the queue, since both rules are honesty markers.
- Outside this story: moving-day and mirror-maze sit next to each other in `queue.txt` and are both `ban`.
