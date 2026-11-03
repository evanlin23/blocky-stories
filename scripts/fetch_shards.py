"""Download the drawn shards an earlier run kept: REUSE is plan_renders.py's JSON {shard: artifact id}.

    REUSE='{"3": 123}' REPO=owner/name python scripts/fetch_shards.py <story>

Each artifact is a zip of that shard's PNGs; they land in out/work/<story>/frames/, where the assemble step expects every
frame. Needs GH_TOKEN (actions: read). A shard that can't be fetched fails the job: assemble would otherwise stop at
"every frame must be there" anyway."""

import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

story = sys.argv[1]
reuse = json.loads(os.environ.get("REUSE") or "{}")
out = Path("out/work") / story / "frames"
out.mkdir(parents=True, exist_ok=True)
for k, art in sorted(reuse.items(), key=lambda kv: int(kv[0])):
    z = out / f"_shard{k}.zip"
    with open(z, "wb") as f:
        subprocess.run(["gh", "api", f"repos/{os.environ['REPO']}/actions/artifacts/{art}/zip"], stdout=f, check=True)
    with zipfile.ZipFile(z) as zf:
        zf.extractall(out)
    z.unlink()
    print(f"shard {k}: artifact {art}")
