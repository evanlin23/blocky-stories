# ep52-ferry-crossing: standards, round 4

Verdict: revise

Checked: story.json, package.json, script.md, the preview contact sheet, the stills sheet, frames pulled from the preview, preflight and check. Passes: fiction (no set text, blank windows and phone), kids (all adults, the Shrug never touches Gran), IP (our own faces, no game names), and originality. The new title and L01 share nothing with ep41-orchard-rows or with any queued title or line 1. Flash: preflight PASS (4205 frames). The worst moment is 3 flashes a second at 128.6 s (the S84 to S85/S86 cuts onto the window and the glowing orange armrest strokes). Actions will re-measure it, so this isn't a must-fix. Opening `if` matches L01 and doesn't repeat any queued shape next to it.

Must-fix:
1. **script.md is out of date and contradicts the build.** L01 and L02, the Rule bullet, "Opening recipe fix" and "First line" all still say "Never drop anything here unless you want it back." / "It hops home after you." (a `ban`). Change them to the built L01 "If you DROP / something HERE / it HOPS home / after YOU." and L02 "Even the things / you meant / to LOSE.". Also match L13 ("a HOLE"), L42 ("town's SLIPWAY"), L57 ("quit") and L58 ("I go to") to story.json.
2. **L36, US English:** "outside my FLAT / in TOWN" becomes "outside my PLACE / in TOWN". Re-voice that one line.
3. **cover_s 0.8:** that frame shows the glove woman's face with no glove in sight, because the green glove disappears against her green coat. Pick a frame where the glove (the title's subject) or the lit Shrug reads clearly, for example S61 at about 90 s.
4. **HANDOFF.md:** delete it before merge. It's a session note with a working path, cover 1.3 and "L07 still says lead", all out of date.

Nice-to-haves:
- story.json `premise` says "harbour". Use "harbor".
- Queue note, not this story's fix: moving-day and mirror-maze are both `ban` and sit next to each other in queue.txt. Putting ep52 (`if`) between them fixes that.
