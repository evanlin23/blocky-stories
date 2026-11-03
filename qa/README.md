# Film checks

Owner, 2026-11-03: "We should ensure everything is good before we publish." And: "why are stuff still failing?
don't we do the rendering? or we should know before we do rendering right?"

Two stages, one file per story (the newest check wins; git history keeps the older ones):

- **proof**, before merge: the qa agent checks the `proof-<story>` artifact that `.github/workflows/proof.yml`
  drew on the PR (the whole film, every drawing the final makes, at half size, with the real voice and mix).
  `{"stage": "proof", "film": "proof-<run id>", "run": <run id>, "sha": "<the commit it drew>", ...}`. `test`
  (`python -m blocky gate <story> --merge`) blocks the merge without a passed one covering the story's current
  film files. RULES.md, 2026-11-03: no story merges without a passed proof qa.
- **final**, before the upload: a short confirm on the `film-<story>` artifact (what the proof couldn't show:
  fine detail, a texture, a sharpening halo, and the craft numbers again).

The daily upload only takes a story whose `qa/<story>.json` passed **that exact film** at stage final. A re-render makes a new
artifact id, so a re-rendered story needs a new check. This folder sits outside `stories/` on purpose, so writing
a check never triggers a re-render.

```json
{"film": 1234567890, "verdict": "pass", "date": "2026-11-03", "checked": ["frames", "first 3 s", "audio", "craft", "flash", "package"], "craft": "| metric | value | target | |\n...", "notes": "..."}
```
`craft` is `scripts/measure.py`'s table for the film (`docs/research/craft-metrics.md`). Its targets warn until the hit data confirms them.
`film` is the `film-<story>` artifact id (or `"legacy"` for the two finals in `legacy/`). `verdict` is `pass` or `fail`.

How to check: `.claude/agents/qa.md`. A `fail` names what to fix. The builder fixes it, the merge re-renders it,
and the new film gets a new check.
