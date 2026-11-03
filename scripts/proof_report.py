"""The proof's verdict for one story (proof.yml): the craft blocks, the flash bar, the loudness and the clip check,
as a markdown job summary. Exits 1 on a craft block, a flash failure or a head clipping through something.

    python scripts/proof_report.py --story NAME --dir <folder with craft.json, flash.json, mix.json, clip.json,
                                   proof.json> [--summary $GITHUB_STEP_SUMMARY]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def _load(p: Path):
    return json.loads(p.read_text()) if p.exists() else None


def verdict(craft: dict | None, flash: dict | None, mix: dict | None, clip: dict | None,
            clip_ok: list[str] | None = None) -> tuple[bool, list[str]]:
    """(passes, the reasons it fails). A missing report fails: the proof didn't finish."""
    from blocky.checks import clip_problems

    why = []
    if craft is None:
        why.append("no craft numbers (measure.py didn't run)")
    else:
        for c in craft.get("checks", []):
            if c["status"] == "block":
                rng = f"{'' if c['low'] is None else c['low']}–{'' if c['high'] is None else c['high']}"
                why.append(f"craft block: {c['metric']} = {c['value']} (target {rng})")
    if flash is None:
        why.append("no flash report")
    elif not flash.get("house_bar", {}).get("pass"):
        why.append("flash: fails the house bar " + json.dumps(flash.get("house_bar", {}))[:300])
    if clip is None:
        why.append("no clip check")
    else:
        why += [f"clip: {m}" for m in clip_problems(clip.get("hits", []), clip_ok)]
        if clip.get("error"):
            why.append(f"clip check failed to run: {clip['error']}")
    f = (mix or {}).get("file") or {}
    if f.get("true_peak_dbtp") is not None and f["true_peak_dbtp"] > -1.0:
        why.append(f"true peak {f['true_peak_dbtp']} dBTP (at most -1)")
    return not why, why


def markdown(story: str, ok: bool, why: list[str], craft_table: str, mix: dict | None, proof: dict | None) -> str:
    f = (mix or {}).get("file") or {}
    p = proof or {}
    lines = [f"## Proof: {story}: {'PASS' if ok else 'FAIL'}", "",
             f"Drawn from `{p.get('sha', '?')[:9]}` (run {p.get('run_id', '?')}), the final's drawings at "
             f"{p.get('res', '270x480')}, {p.get('frames', '?')} frames in {p.get('shards', '?')} shards. "
             f"Wall time {p.get('minutes', '?')} min.", "",
             f"Loudness {f.get('lufs')} LUFS, true peak {f.get('true_peak_dbtp')} dBTP.", ""]
    if why:
        lines += ["**Must fix before merge:**", *[f"- {w}" for w in why], ""]
    lines += [craft_table, "", "Next: the qa agent checks this proof (`.claude/agents/qa.md`, stage proof) and writes "
              f"`qa/{story}.json`. The story merges only on a passed proof check."]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--story", required=True)
    ap.add_argument("--dir", type=Path, required=True)
    ap.add_argument("--summary", type=Path)
    a = ap.parse_args(argv)
    craft = _load(a.dir / "craft.json")
    flash, mix, clip, proof = (_load(a.dir / n) for n in ("flash.json", "mix.json", "clip.json", "proof.json"))
    table = ""
    if craft is not None:
        import measure
        table = measure.table(craft)
    st = _load(Path("stories") / a.story / "story.json") or {}
    ok, why = verdict(craft, flash, mix, clip, st.get("clip_ok"))
    md = markdown(a.story, ok, why, table, mix, proof)
    (a.dir / "verdict.json").write_text(json.dumps({"pass": ok, "why": why}, indent=1))
    if a.summary:
        with open(a.summary, "a") as fh:
            fh.write(md + "\n")
    print(md)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
