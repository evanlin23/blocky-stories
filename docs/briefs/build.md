<!-- The build brief for one story (rewrite plan step 5: sessions start with a brief name, not a pasted brief). A session's prompt gives __STORY__, __TITLE__ and __BATCH__. -->

You are a delegated session of the SECOND ORCHESTRATOR for evanlin23/blocky-stories, the repo behind the YouTube channel Buhtown (@Buhtown): creepy blocky story Shorts made in Blender, voiced with Kokoro TTS and rendered on GitHub Actions.

You have ONE job: build one new story, __STORY__ ("__TITLE__"), from its merged script. Get it reviewed and proofed, then merge it or drop it. When its PR merges or the story is dropped, you are done. Don't take on anything else.

It's one of batch __BATCH__; your prompt says where the batch came from. Its pitch, shape, lane, length arm and look are in the header of stories/__STORY__/script.md.

The owner: "We shouldn't upload anything that isnt good... it will be more harmful if we uplaod soemthing that performs poorly right?" Sunk cost never counts.

## Read first
- CLAUDE.md.
- RULES.md, which outranks everything except the owner's words. Read especially "The audit decisions (owner, 2026-11-04)".
- docs/operations.md: the Renders, Proofs and Merging sections.
- stories/__STORY__/script.md and package.json.
- .claude/agents/builder.md, critic.md, standards.md and qa.md.

The builder reads docs/engine.md itself.

## Branch and identity
- Branch `claude/batch__BATCH__-__STORY__`, created off origin/main. Push only to it, with `git push -u origin claude/batch__BATCH__-__STORY__`.
- Set your identity: `git config user.name evanlin23 && git config user.email 113861384+evanlin23@users.noreply.github.com`
- The container can be reclaimed at any time, so commit and push a WIP checkpoint after every phase.
- Never end your turn while you wait on a proof run, a `test` check or a long render: nothing wakes an idle session when the run finishes. Wait with a Monitor (or Bash `run_in_background`) until-loop that exits when the run's status is completed, then act on the result (2026-11-04: ep83 sat idle for 2 hours on a failed proof).
- Before every review, proof check or qa, merge the latest origin/main into your branch (owner rule).

## Steps
1. **Set up.** Run `git fetch origin && git checkout -b claude/batch__BATCH__-__STORY__ origin/main`, then `bash blocky/setup.sh`, and export what it prints (BLOCKY_BPY, BLOCKY_TTS).

2. **Build** (/week step 2). Use a FRESH `builder` agent for each phase: the build, then each fix round. Never reuse one builder across phases. The build follows builder.md in order.
   - **Creature test, only if the script has a creature on screen.** Two fresh `critic` agents (model "opus") judge that one still at phone size. Both must score it at least 7 and call it frightening. Allow three tries at most, then drop. Stories are creature-light by default (audit decision 4), so most skip this.
   - **Story files.** generator/make_story.py and lines.json write story.json, with "look": {"polish": true, "flash_safe": true}, plus any look keys the script header names. Then set.py, then the voice.
   - **Preflight.** Run `python -m blocky preflight __STORY__` until it shows 0 blocks. A still over 1.0 s blocks. Put a shot that set.py animates in "set_moves".
   - **Stills sheet and framing pre-check (added 2026-11-04).** The builder makes a stills sheet of the key beats at phone size. Then ONE fresh `critic` (model "opus") looks at that sheet for framing ONLY:
     - every head on screen whole;
     - each face at least 1/5 of the frame width;
     - the hands or object each line names, in frame;
     - nothing the line is about cut at a frame edge or lost in the dark;
     - nothing that reads as the wrong thing at phone size.

     The builder fixes what it lists before the preview. This is not a review round, it gives no verdict, and it's done once. Framing and faces at phone size were the most common blockers in batches 7 to 9.
   - **Framing lint, every shot.** Run `python scripts/framing.py --story stories/__STORY__` (report-only; on main since #284). Have the builder fix every finding: a head cut by any frame edge, a face under 1/5 of the width on a line about that person, back-of-head or a profile (the narrator's too, on an I / me / my line), an empty frame during a line, a mouth under the caption, a hand or the rule tag over a face, or a CAPS word's prop never in frame. List a deliberate one in story.json `"framing_ok"`. Run it again before every review round and before the rescue.
   - **Preview.** Render the preview, then finish and mix.
   - **Frame lint, on the preview.** Run `python scripts/frames.py --story stories/__STORY__` on the preview's frames before every review round, next to framing.py (report-only, lesson 40). Have the builder fix every finding: blank or near-uniform frames (a camera inside a wall), a pop on a shot's first drawing (a character posed a frame late), or a shot that opens dark and brightens over its first 0.3 s (a light fading in after the cut). List a deliberate one in story.json `"frames_ok"`.
   - **Flash.** Run `python -m blocky flash __STORY__ --like-proof` (every drawing the proof draws, at the meter's size: it reads what the proof reads, 2026-11-05) on any story with bright light changes, glows or flipping lights, and pass with margin (at most about 5 flashes a second, against the cap of 6). The first full `--like-proof` draws every frame and can take over 30 minutes: run it in the background with a 2 h timeout and wait with a Monitor. After a fix, re-check with `--like-proof --shots <the changed shots>`, which keeps the other drawings (lesson 41). A swinging, flickering or switching practical light counts (2026-11-04: ep97 failed its proof at 7 a second from a swinging bulb).
   - **Measure, on the preview film.** Run `python scripts/measure.py --story stories/__STORY__` after the preview is
     finished and mixed: it measures `out/work/__STORY__/<slug>-preview.mp4`. With no film the 4 craft blocks read
     `unmeasured`, which is not a pass (until 2026-11-06 they were silently left out, and ep117 passed "locally" at
     12.5 against 14; lesson 43). The 4 craft blocks must pass, with these margins for what the proof and the final
     will read (measured on 8 proofs, 7 of them against their finals):
     - picture changes per 10 s at 0.5 s: the preview differs from the proof by up to 1.0 either way, so 13.5 or
       more on the preview; the proof and the final read the same;
     - picture changes per 10 s at 0.25 s: the preview within about 0.7 of the proof, the final within 0.2 of it,
       so 15 on the preview;
     - motion energy: the preview within about 0.4 of the proof, the final within 0.05, so 6.4 on the preview;
     - longest still ≤1.0 s, and **`longest_still_q_edge_s` ≤1.0 s too**: a still at the threshold's edge reads
       one 0.27 s step longer on the less noisy final (ep126: 0.8 s on the proof, 1.07 s, a block, on the final).
       The longest still moves in 0.27 s steps (8 frames), so 0.8 s is the most that passes.

     On a pace fail, shorten the quiet span or add motion inside it. Never crop harder.
   - **Sound.** The budget is 2 to 4 events per 10 s, and the score plays under the whole film.

3. **Reviews** (/week step 3). Spawn `critic` and `standards`, each with model "opus". Round 1 walks every shot. Round 2 and the rescue look check only the last round's must-fixes and regressions, and new non-severe findings are should-fix (RULES, audit decision 8). Pass this rule to each reviewer in its prompt.
   - **Rounds:** TWO ROUNDS AT MOST, plus at most ONE single-fix rescue, with no exceptions (RULES, audit decision 3). Round 2 re-runs only the reviewer that said revise.
   - **The rescue:** only if a review names a single concrete fix. The builder applies just that, and only the reviewer who blocked looks once more. Apply the fix to every shot of the same line or beat, not just the shot the review names (2026-11-04: ep108's rescue fixed S40 and missed S41, its twin).
   - **Must-fixes:** send words, title or package notes to the `writer` agent (model "opus") first. Then send every must-fix to one fresh builder in one call.
   - **Dropping:** if the story isn't approved after that, or a reviewer says kill:
     - commit and push everything;
     - write stories/__STORY__/HANDOFF.md with why: the open must-fixes and the scores;
     - stop with STATUS dropped.

     Don't open a PR for a dropped story.

4. **On approval.** Remove `"hold"` from package.json, then run:
   - `python -m blocky check __STORY__`
   - `python -m blocky gate __STORY__`, which must say OPEN
   - `python -m pytest -q`

5. **Open the PR.** Use the GitHub MCP tools, with the title "__STORY__: build (batch __BATCH__)", not WIP. In the body, add any queue-spacing notes standards gave.
   - proof.yml draws the proof on the PR once both reviews approve. That's the whole film at 270x480 with the real voice and mix, kept as the artifact `proof-__STORY__`. It takes about 25 to 40 min on 8 runners, and it may queue behind other runs, which is fine.
   - Check that the run actually drew: a real proof has voice, draw, clip and assemble jobs.
   - If it only ran `plan`, start it by hand with GitHub MCP `actions_run_trigger`: method run_workflow, workflow_id proof.yml, ref = your branch, inputs {"story": "__STORY__"}. Dispatching proof.yml is allowed.
   - Never dispatch render.yml or upload.yml, and never cancel any run.

6. **Proof qa.** Run the `qa` agent (model "opus") at stage "proof" on the newest `proof-__STORY__` artifact.
   - Get the artifact's download URL with the GitHub MCP tool `actions_get`, method `download_workflow_run_artifact`, and curl it into a scratch folder. gh api is blocked by the proxy for Actions. Give the qa agent the local path.
   - The qa agent writes qa/__STORY__.json with "stage": "proof", film, run and sha. Commit it on the PR branch.
   - The proof also fails by itself on any of these:
     - a craft block;
     - flash;
     - a head clip (`python -m blocky clipcheck`; an intended overlap goes in story.json "clip_ok": ["S12/ring"]);
     - true peak over -1 dBTP.

7. **Merge.** Merge the PR only when the proof qa passed AND the PR's `test` check run has concluded success. Read the conclusion; never merge red or in progress. If the proof or its qa fails, fix it only if the fix fits inside the round cap above; otherwise drop as in step 3.

8. **After the merge.** The merge starts the final render on Actions by itself, and the QA desk checks the final. Don't add the story to queue.txt: the first orchestrator alone owns the queue.

## Story rules (RULES.md has the full list)
- **Opening:** line 1 is a warning or a concrete threat to the narrator or "you". It plays over a close-up first shot (no wide or establishing shot in the first 3 s), lit to read on a phone, with a sound hit on its last word. The opening swoosh is kept.
- **Keep from the script:** its shape and `"opening"`. Every title has exactly one CAPS word and one emoji at the end (owner rule).
- **On screen:** bright and saturated by default, with the rule marker on screen the whole time and a cut or punch-in every 1 to 2 s. Keep the loop ending and the quotable line.
- **Content:** no Roblox names or assets, no children in the cast, everything made up, and no real words or signs in the set. Assets are CC0 (assets/LICENSES.md), and the music is our own synthesized score. No downloaded creature meshes.
- **Files:** no machine-specific paths in committed files. Use US English in lines, titles and pins.

## Never touch
- queue.txt, uploads.json, pulled.json, other stories' qa/ files, .github/workflows/*.yml, docs/second-team.md, issue #177.
- blocky/, meaning any engine file. If an engine bug blocks you, write it in HANDOFF.md and report it.
- Every story folder except stories/__STORY__/. Touch stories/ideas.md and stories/lore.md only if a reviewer requires it.
- Runs: never dispatch render.yml or upload.yml, never cancel any run, and dispatch proof.yml only as step 5 says. Never upload.

## Budget
- $0: free tools only.
- The weekly usage limit is shared with other sessions. Keep your context small: read verdict lines and must-fix lists, not whole reviews or code.
- If you see a usage-limit warning, commit and push a WIP checkpoint, write HANDOFF.md with exactly where you stopped, and stop.
- Never paste secrets.

## Report
Keep HANDOFF.md current. End your final message with exactly:
STATUS: <working|merged|dropped|blocked>
PR: <url or none>
NEXT: <one line>
WHY: <one line: the last verdicts and scores, the proof qa result, or what blocked you>
