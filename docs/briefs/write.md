<!-- The batch writing brief (rewrite plan step 5). A session's prompt gives __BATCH__, __N__, the first episode number __FIRST__ and any batch notes. -->

You are a delegated session of the SECOND ORCHESTRATOR for evanlin23/blocky-stories, the repo behind the YouTube channel Buhtown (@Buhtown): creepy blocky story Shorts made in Blender. You have ONE job: write batch __BATCH__, __N__ new stories numbered from ep__FIRST__. Each gets its script, plan and package, held until built. Merge them in one PR, and then you're done.

The owner: "We shouldn't upload anything that isnt good." Sunk cost never counts. A script that can't clear the panel is cut, not padded.

## Read first
- CLAUDE.md.
- RULES.md, which outranks everything except the owner's words. Read especially "The audit decisions (owner, 2026-11-04)".
- .claude/skills/week/SKILL.md, step 1.
- .claude/agents/writer.md.
- docs/research/premise-engines.md.
- docs/research/creature-playbook.md.
- metrics/summary.md, if it exists.
- stories/ideas.md: the "killed" lines and the "Made" rows.

## Steps
1. **Set up.** Run `git fetch origin && git checkout -b claude/batch__BATCH__-scripts origin/main`. Set your identity: `git config user.name evanlin23 && git config user.email 113861384+evanlin23@users.noreply.github.com`.
2. **Pitch.** Use one `writer` agent (model "opus") to pitch about twice as many ideas as you need.
   - Sources: premise engines not yet used (check every "Made" row and every story folder), plus the best "can be tried again" killed lines, re-imagined with a new execution (never a twist killed for a hard rule).
   - Movie-level premises from proven engines, never a specific work.
   - **Creature-light by default** (audit decision 4): a person made wrong, or a creature never fully shown. At most one full creature reveal in the batch, and its card names why it's worth it.
   - Plan every beat so faces and hands read at phone size: framing and faces were the most common blockers in batches 7 to 9.
   - **The 2026-11-12 bar** (writer.md, its last section): about half warm reveals (ep124's kind) beside eerie ones; one or two ultra-short puzzles at 30 to 45 s; the interactive lane; one repeatable format; by 0:05 me/mine or a job for the viewer; no backstory before 0:15; fact titles; a real-question pin.
3. **Panel.** Run a blind panel of fresh `critic` agents (model "opus") on the pitches' first lines and premises, as batch 10 did. Keep the best __N__. The batch rules in writer.md apply: no two share a setting, creature, first-line type, ending shape or kind of warmth, and the openings are spread across shapes.
4. **Script.** Have the writer script, plan and package each one. Each package.json has `"hold": "batch __BATCH__: scripts only, not built yet"`. Every title has exactly one CAPS word and one emoji at the end. Use US English.
5. **Check.** Run one `standards` agent (model "opus") over the batch for originality against every earlier story, fiction, IP and kids. Apply its must-fixes through the writer once.
6. **Merge.**
   - Run `python -m pytest -q`.
   - Open one PR, "Batch __BATCH__ scripts: <one line>", with the GitHub MCP tools.
   - Merge it when its `test` check has concluded success. Never merge red.

## Never touch
queue.txt, uploads.json, pulled.json, qa/, .github/, blocky/, docs/second-team.md, issue #177, and every existing story folder. Never dispatch or cancel any workflow run.

## Budget
- $0: free tools only.
- The usage limit is shared, so keep your context small.
- If you see a usage-limit warning, commit and push a WIP checkpoint and stop.

## Report
End with:
STATUS: <merged|blocked>
PR: <url>
NEXT: <one line>
WHY: <the stories, one line each: slug, opening shape, lane, length arm, panel score>
