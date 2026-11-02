"""python -m blocky <step> <story>: one creepy blocky story, end to end. See README.md.

The story lives in `stories/<story>/` (story.json and its own set.py). Working files go to
`out/work/<story>/` (gitignored), and the finished reel to `out/<slug>.mp4`.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / "out"
QUALITY = {
    # the preview draws every 4th frame small; the final draws each shot on its own step (most on twos, the
    # chases and hits on ones) at 540 x 960, and post scales it to 1080 x 1920
    "preview": {"res": [270, 480], "samples": 4, "step": 4},
    "final": {"res": [540, 960], "samples": 10, "step": None},
}
WORKERS = int(os.environ.get("BLOCKY_WORKERS", 2))   # Blender processes
THREADS = int(os.environ.get("BLOCKY_THREADS", 2))   # render threads each (4 cores)


def work(story: str) -> Path:
    d = OUT / "work" / story
    d.mkdir(parents=True, exist_ok=True)
    return d


def tts_python() -> str:
    exe = os.environ.get("BLOCKY_TTS")
    if not exe or not Path(exe).exists():
        sys.exit("set BLOCKY_TTS to the Python of a venv with kokoro, torch and faster-whisper (README.md)")
    return exe


def bpy_python() -> str:
    exe = os.environ.get("BLOCKY_BPY") or os.environ.get("CLAY_BPY")
    if not exe or not Path(exe).exists():
        sys.exit("set BLOCKY_BPY to the Python of a venv with Blender's bpy module (README.md)")
    return exe


def story_json(story: str) -> dict:
    from blocky.timeline import load_story

    return load_story(story)


def cmd_voice(a):
    from blocky.timeline import story_dir

    vo = work(a.story) / "vo"
    args = [tts_python(), str(HERE / "voice.py"), "synth", str(story_dir(a.story)), "--out", str(vo)]
    if a.only:
        args += ["--only", a.only]
    subprocess.run(args, check=True, env={**os.environ, "OMP_NUM_THREADS": "4"})
    if a.verify:   # CI: re-make the narration, but the kept timings set the edit; fail if they drift a frame
        sys.exit(verify_voice(vo / "voice.json", story_dir(a.story) / "voice-timings.json"))
    # the word timings (no audio) are kept with the story: they set the edit, so the picture rebuilds without TTS
    shutil.copy2(vo / "voice.json", story_dir(a.story) / "voice-timings.json")
    cmd_timeline(a)


def verify_voice(new: Path, kept: Path, tol: float = 1 / 30) -> int:
    n, k = json.loads(new.read_text())["lines"], json.loads(kept.read_text())["lines"]
    bad = []
    # compare the lines the story has now (the new run); the kept file may still hold lines cut in revisions
    for lid, nv in n.items():
        kv = k.get(lid)
        if kv is None:
            bad.append(f"{lid}: not in the kept timings")
            continue
        pairs = [(nv["dur"], kv["dur"])] + [(x, y) for a_, b_ in zip(nv["chunks"], kv["chunks"]) for x, y in zip(a_, b_)]
        worst = max(abs(x - y) for x, y in pairs)
        if worst > tol or len(nv["chunks"]) != len(kv["chunks"]):
            bad.append(f"{lid}: drifts {worst:.3f} s")
    for b in bad:
        print("voice drift:", b)
    print("voice: matches the kept timings" if not bad else f"voice: {len(bad)} line(s) drift; re-run `voice` locally")
    return 1 if bad else 0


def cmd_timeline(a):
    from blocky import timeline

    # the kept timings set the edit (`voice` refreshes them); the working copy is only a fallback
    src = timeline.story_dir(a.story) / "voice-timings.json"
    if not src.exists():
        src = work(a.story) / "vo" / "voice.json"
    tl = timeline.write(a.story, src, work(a.story) / "timeline.json")
    words = sum(len(tl["lines"][l].get("text", "").split()) for l in tl["order"])
    print(f"timeline: {tl['duration']} s, {tl['frames']} frames, {len(tl['shots'])} shots, "
          f"{len(tl['captions'])} captions, {words / tl['duration'] * 60:.0f} wpm overall")
    return tl


def blender(job: dict, tag: str, workers: int = 1) -> float:
    w = work(job["story"])
    t0 = time.time()
    frames = job.get("frames")
    n = workers if frames and len(frames) > 1 else 1
    procs = []
    for k in range(n):
        jw = dict(job)
        if n > 1:
            jw["frames"] = frames[k::n]
        jp = w / f"job-{tag}-{k}.json"
        jp.write_text(json.dumps(jw))
        log = open(w / f"blender-{tag}-{k}.log", "w")
        env = {**os.environ, "OMP_NUM_THREADS": str(jw.get("threads", 2))}
        procs.append((subprocess.Popen([bpy_python(), str(HERE / "bl_story.py"), str(jp)], stdout=log,
                                       stderr=subprocess.STDOUT, env=env), k))
    bad = [k for p, k in procs if p.wait() != 0]
    if bad:
        sys.exit(f"Blender failed, see {w}/blender-{tag}-{bad[0]}.log")
    return time.time() - t0


def base_job(a, q) -> dict:
    from blocky.timeline import story_dir

    w = work(a.story)
    return {"story": a.story, "story_dir": str(story_dir(a.story)), "timeline": str(w / "timeline.json"),
            "res": q["res"], "samples": getattr(a, "samples", None) or q["samples"], "threads": THREADS}


def cmd_render(a):
    from blocky import timeline

    q = QUALITY["preview" if a.preview else "final"]
    w = work(a.story)
    tl = json.loads((w / "timeline.json").read_text())
    frames = timeline.frame_list(tl, q["step"])
    if a.shots:
        keep = set(a.shots.split(","))
        frames = [f for f in frames for s in tl["shots"] if s["id"] in keep and s["f0"] <= f < s["f1"]]
    if a.only:
        frames = [int(x) for x in a.only.split(",")]
    if a.shard:   # "k/n": this machine draws every n-th frame from k (GitHub Actions splits a film this way)
        k, n = (int(x) for x in a.shard.split("/"))
        frames = frames[k::n]
    d = w / ("frames-preview" if a.preview else "frames")
    job = {**base_job(a, q), "out": str(d), "frames": frames, "skip_existing": not a.force}
    dt = blender(job, "preview" if a.preview else "final", WORKERS)
    print(f"rendered {len(frames)} frames in {dt / 60:.1f} min -> {d}")
    log = d / "render-time.json"
    prev = json.loads(log.read_text()) if log.exists() else {"runs": []}
    prev["runs"].append({"frames": len(frames), "minutes": round(dt / 60, 1), "res": q["res"],
                         "samples": job["samples"], "shots": a.shots or "all"})
    log.write_text(json.dumps(prev, indent=1))


def cmd_stills(a):
    from PIL import Image

    from blocky import post

    tl = json.loads((work(a.story) / "timeline.json").read_text())
    st = story_json(a.story)
    ts = [float(x) for x in a.t.split(",")]
    w_, h_ = (int(v) for v in a.res.split("x"))
    d = work(a.story) / "stills"
    job = {**base_job(a, {"res": [w_, h_], "samples": a.samples}), "out": str(d), "stills": ts}
    dt = blender(job, "stills")
    ims = []
    for t in ts:
        f = int(round(t * tl["fps"]))
        img = post.finish(tl, st, f, d / f"f{f:05d}.png", post.Rain() if st.get("rain_shots") else None)
        Image.fromarray(img).save(d / f"post-{f:05d}.png")
        ims.append(Image.fromarray(img).resize((360, 640)))
    sheet = Image.new("RGB", (360 * len(ims), 640))
    for i, im in enumerate(ims):
        sheet.paste(im, (360 * i, 0))
    sheet.save(d / "sheet.png")
    print(f"{len(ts)} stills in {dt:.0f} s -> {d / 'sheet.png'}")


def cmd_finish(a):
    from blocky import post

    w = work(a.story)
    tl = json.loads((w / "timeline.json").read_text())
    d = w / ("frames-preview" if a.preview else "frames")
    out = w / ("picture-preview.mp4" if a.preview else "picture.mp4")
    t0 = time.time()
    post.encode(tl, story_json(a.story), d, out)
    print(f"picture {out} in {time.time() - t0:.0f} s")


def contact(video: Path, tl: dict, audio, path: Path, title: str) -> None:
    """15 frames across the film with their time, shot and caption, over the mix's spectrogram."""
    from io import BytesIO

    import numpy as np
    from PIL import Image, ImageDraw

    from blocky.synth import SR

    n, tw, th, cols = 15, 216, 384, 5
    times = [0.4 + i * (tl["duration"] - 0.8) / (n - 1) for i in range(n)]
    spec_h = 200
    sheet = Image.new("RGB", (cols * (tw + 8) + 8, 3 * (th + 30) + 40 + spec_h + 20), (22, 20, 28))
    d = ImageDraw.Draw(sheet)
    d.text((10, 10), title, fill=(240, 236, 228))
    for i, t in enumerate(times):
        png = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1",
                              "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True, check=True).stdout
        im = Image.open(BytesIO(png)).convert("RGB").resize((tw, th), Image.BILINEAR)
        x, y = 8 + (i % cols) * (tw + 8), 34 + (i // cols) * (th + 30)
        sheet.paste(im, (x, y + 18))
        sid = next((s["id"] for s in tl["shots"] if s["start"] <= t < s["end"]), "")
        cap = next((c["text"] for c in tl["captions"] if c["start"] <= t < c["end"]), "")
        d.text((x, y + 2), f"{t:5.1f}s {sid} {cap}"[:34], fill=(230, 225, 215))
    mono = audio.mean(axis=1)
    nfft, hop = 2048, 512
    fr = np.lib.stride_tricks.sliding_window_view(mono, nfft)[::hop] * np.hanning(nfft)
    S = 20 * np.log10(np.abs(np.fft.rfft(fr, axis=1)) + 1e-9).T
    f = np.fft.rfftfreq(nfft, 1 / SR)
    S = S[np.searchsorted(f, np.geomspace(40, 16000, spec_h))][::-1]
    S = np.clip((S - S.max() + 85) / 85, 0, 1)
    img = (np.stack([S ** 0.8, S ** 1.6 * 0.8, S ** 3 * 0.5], -1) * 255).astype(np.uint8)
    sw = sheet.width - 16
    y0 = sheet.height - spec_h - 12
    sheet.paste(Image.fromarray(img).resize((sw, spec_h)), (8, y0))
    for s in tl["shots"]:
        x = 8 + int(s["start"] / tl["duration"] * sw)
        d.line([(x, y0), (x, y0 + spec_h)], fill=(255, 255, 255), width=1)
    sheet.save(path)


def cmd_mix(a):
    from blocky import encode as penc
    from blocky import sound

    w = work(a.story)
    st = story_json(a.story)
    tl = json.loads((w / "timeline.json").read_text())
    picture = w / ("picture-preview.mp4" if a.preview else "picture.mp4")
    t0 = time.time()
    audio, stats = sound.mix(tl, st, w / "vo")
    wav = w / "mix.wav"
    slug = st.get("slug", a.story)
    mp4 = w / f"{slug}-preview.mp4" if a.preview else OUT / f"{slug}.mp4"

    def measure(x):   # the true peak of the finished file, after the AAC encode
        penc.write_wav(wav, x)
        penc.mux(picture, wav, mp4)
        return penc.ebur128(mp4)["true_peak_dbtp"]

    audio, stats["file_peak_tries"] = sound.fit_file_peak(audio, measure)
    stats["file"] = penc.ebur128(mp4)
    stats["mix_s"] = round(time.time() - t0, 1)
    contact(mp4, tl, audio, mp4.with_suffix(".contact.png"),
            f"{slug}  {tl['duration']:.1f}s  {stats['file']['lufs']} LUFS  {stats['file']['true_peak_dbtp']} dBTP")
    (w / f"mix{'-preview' if a.preview else ''}.json").write_text(json.dumps(stats, indent=1))
    print(mp4, stats)


def cmd_soundtest(a):
    """The look test's voice half: the first N seconds of the mix (narrator, score, ambience) as an m4a."""
    from blocky import encode as penc
    from blocky import sound

    w = work(a.story)
    st = story_json(a.story)
    tl = json.loads((w / "timeline.json").read_text())
    audio, stats = sound.mix(tl, st, w / "vo")
    n = int(a.seconds * 48000)
    wav = w / "soundtest.wav"
    penc.write_wav(wav, audio[:n] * __import__("numpy").minimum(1, (n - __import__("numpy").arange(n)) / 9600)[:, None])
    out = Path(a.out) if a.out else w / "soundtest.m4a"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(wav), "-c:a", "aac", "-b:a", "192k", str(out)],
                   check=True)
    print(out, stats["lufs"])


def cmd_asr(a):
    from blocky import encode as penc
    from blocky import sound

    w = work(a.story)
    tl = json.loads((w / "timeline.json").read_text())
    vo, _ = sound.narration(tl, w / "vo")
    import numpy as np

    penc.write_wav(w / "narration-only.wav", np.stack([vo, vo], 1) * 0.5)
    subprocess.run([tts_python(), str(HERE / "voice.py"), "asr", str(w / "narration-only.wav"), str(w / "timeline.json")],
                   env={**os.environ, "OMP_NUM_THREADS": "4",
                        **({"BLOCKY_ASR_TAIL": "1"} if story_json(a.story).get("asr_ignore_tail_repeat") else {})})


def cmd_check(a):
    from blocky import checks

    tlp = work(a.story) / "timeline.json"
    problems = checks.run(a.story, tlp if tlp.exists() else None)
    for p in problems:
        print("BLOCK" if p[0] == "block" else "warn ", p[1])
    if not problems:
        print("no problems")
    sys.exit(1 if any(p[0] == "block" for p in problems) else 0)


def cmd_flash(a):
    from blocky import flash

    w = work(a.story)
    st = story_json(a.story)
    mp4 = Path(a.file) if a.file else OUT / f"{st.get('slug', a.story)}.mp4"
    rep = flash.run(mp4, w / "timeline.json")
    sys.exit(0 if rep["house_bar"]["pass"] else 1)


def cmd_gate(a):
    from blocky import gate

    cmd_timeline(a)
    ok, problems = gate.run(a.story, work(a.story) / "timeline.json")
    for p in problems:
        print("BLOCK" if p[0] == "block" else "warn ", p[1])
    print(f"gate {a.story}: {'OPEN' if ok else 'CLOSED'}")
    sys.exit(0 if ok else 1)


def cmd_preflight(a):
    """Every automatic check in one go, so nobody runs them one by one: timeline, check, package lint, the Whisper
    word check (when the narration is on disk) and a flash reading of the preview (indicative only: the preview
    holds every 4th drawing). Prints one summary and exits 1 on any block."""
    from blocky import checks, gate

    cmd_timeline(a)
    w = work(a.story)
    rows = [("check", p) for p in checks.run(a.story, w / "timeline.json")]
    pkg = gate.load_package(a.story)
    rows += [("package", p) for p in gate.lint_package(pkg)] if pkg else [("package", ("warn", "no package.json yet"))]
    if os.environ.get("BLOCKY_TTS") and (w / "vo").exists():
        r = subprocess.run([sys.executable, "-m", "blocky", "asr", a.story], capture_output=True, text=True)
        tail = (r.stdout.strip().splitlines() or ["(no output)"])[-1]
        rows.append(("asr", ("pass" if tail.startswith("0 word") else "block", tail)))
    st = story_json(a.story)
    prev = w / f"{st.get('slug', a.story)}-preview.mp4"
    if prev.exists():
        from blocky import flash

        rep = flash.run(prev, w / "timeline.json")
        rows.append(("flash", ("pass" if rep["house_bar"]["pass"] else "warn",
                               "preview " + ("passes" if rep["house_bar"]["pass"] else "fails") + " the house bar (indicative)")))
    for v in gate.verdicts(a.story).items():
        rows.append(("review", ("pass" if v[1] and v[1][1] == "approve" else "warn", f"{v[0]}: {v[1] or 'not yet'}")))
    blocks = 0
    for kind, (lvl, msg) in rows:
        if lvl == "block":
            blocks += 1
        if lvl != "pass" or a.verbose:
            print(f"{lvl:5} {kind:8} {msg}")
    print(f"preflight {a.story}: {blocks} block(s)")
    sys.exit(1 if blocks else 0)


def main():
    ap = argparse.ArgumentParser(prog="python -m blocky")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, **kw):
        p = sub.add_parser(name, **kw)
        p.add_argument("story")
        return p

    v = add("voice")
    v.add_argument("--only")
    v.add_argument("--verify", action="store_true")
    add("timeline")
    s = add("stills")
    s.add_argument("--t", required=True)
    s.add_argument("--res", default="540x960")
    s.add_argument("--samples", type=int, default=16)
    r = add("render")
    r.add_argument("--preview", action="store_true")
    r.add_argument("--shots")
    r.add_argument("--only")
    r.add_argument("--samples", type=int)
    r.add_argument("--force", action="store_true")
    r.add_argument("--shard", help="k/n: draw only every n-th frame starting at k")
    f = add("finish")
    f.add_argument("--preview", action="store_true")
    m = add("mix")
    m.add_argument("--preview", action="store_true")
    t = add("soundtest")
    t.add_argument("--seconds", type=float, default=10.0)
    t.add_argument("--out")
    add("asr")
    add("check")
    fl = add("flash")
    fl.add_argument("--file")
    add("gate")
    pf = add("preflight")
    pf.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    {"voice": cmd_voice, "timeline": cmd_timeline, "stills": cmd_stills, "render": cmd_render, "finish": cmd_finish,
     "mix": cmd_mix, "soundtest": cmd_soundtest, "asr": cmd_asr, "check": cmd_check, "flash": cmd_flash,
     "gate": cmd_gate, "preflight": cmd_preflight}[a.cmd](a)


if __name__ == "__main__":
    main()
