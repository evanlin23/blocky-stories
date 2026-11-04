# ep100-window-bridges handoff

- 2026-11-03: branch claude/batch9-ep100-window-bridges off origin/main. Setup done. Build phase (builder #1) running. No creature, so no creature still test.
- Builder #1 reached a preview ("preview build, camera fixes", 667c7e8), then the container restarted and cut it off. Calm opening (#209) cancelled: keep the polish swoosh. Merged origin/main (7ea0edc). Builder #2 is finishing: preflight, a fresh preview on the new engine, flash, clipcheck, measure.
- Round 1: standards revise (L02 too close to ep97's opening, blank cover, stale hold; queue spacing note for the first orchestrator: keep 4+ slots from ep97, never next to another `count` opening). Critic revise (eerie middle 4, faces 5; S01 tilt, S47/48 Eli upside down, rising bridges never show, memory shot, small faces). Writer applied the words fixes (315e5ff). Fix builder (round 1) is running. Round 2 re-runs both reviewers. It's the last round.

## DROPPED (2026-11-04)
Not approved after the 2-round review limit (no rescue round allowed).
- Round 2 standards: **approve**, no must-fixes (reviews/r2-standards.md). Nice-to-have: soften the flash at S119 to S123 (100 to 107 s) and around 119 s.
- Round 2 critic: **revise** (reviews/r2-critic.md). Scores improved: hook 8, eerie middle 6, faces 6, variety 7, length 9, close-up 7, average about 7.6, nothing under 5. Two open build-only must-fixes:
  1. S138 (116.9 to 119.0 s, L62 "he'll REMEMBER me"): the camera sits under a bridge, so about 2/3 of the frame is a blank plank underside on the payoff line. Raise it to about z 6, looking at Eli's open teal shutters in April light, our bridge in frame, nothing within 0.5 m of the lens.
  2. S109 (92.6 to 95.7 s, L49): 3.1 s of an empty sill. Frame the charred end of the oldest bridge on the sill (at least 1/3 of the frame), or cut at 94.2 s into that framing plus the raised bridges seen from below.
- Not blocking: the narrator's face is side-on in the memory shot (83 to 87 s).
- State: the last preview is 121.8 s, preflight 0 blocks, clipcheck 0, picture changes 18.8 per 10 s, motion energy 10.4, voice-to-bed gap 10.6 dB. `hold` is already removed from package.json. No PR opened.
- If a later session revives it: both fixes are one-shot camera changes in generator/make_story.py, and then it needs a fresh critic review. Queue note (standards): keep it at least 4 slots from ep97-prize-bears and never next to another `count` opening.
- Engine note for the team (not changed here): a `--force` preview leaves stale frames in out/.../frames-preview, and `finish` mixes them in. Delete them before `finish`.
