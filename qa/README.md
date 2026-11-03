# Final-film checks

Owner, 2026-11-03: "We should ensure everything is good before we publish."

The daily upload only takes a story whose `qa/<story>.json` passed **that exact film**. A re-render makes a new
artifact id, so a re-rendered story needs a new check. This folder sits outside `stories/` on purpose, so writing
a check never triggers a re-render.

```json
{"film": 1234567890, "verdict": "pass", "date": "2026-11-03", "checked": ["frames", "first 3 s", "audio", "flash", "package"], "notes": "..."}
```
`film` is the `film-<story>` artifact id (or `"legacy"` for the two finals in `legacy/`). `verdict` is `pass` or `fail`.

How to check: `.claude/agents/qa.md`. A `fail` names what to fix. The builder fixes it, the merge re-renders it,
and the new film gets a new check.
