"""The sped-up storyteller (note 18): Kokoro-82M (Apache 2.0) reads a story one line at a time, then each line is
played faster, which raises its pitch with it, for the rushed, bright narrator these shorts use.

Runs in the TTS venv, not the repo's Python (kokoro, torch, faster-whisper):

    $BLOCKY_TTS blocky/voice.py synth <story dir> --out <dir>
    $BLOCKY_TTS blocky/voice.py asr   <narration wav> <timeline.json>

A story's `voice` sets the narrator: {"voice": "am_adam", "tempo": 1.03, "rate": 1.45}. `tempo` is Kokoro's own
speed (pitch kept) and `rate` is the speed-up (pitch goes up with it), so the pace is about tempo x rate times
the voice's normal pace. A cast member with its own `voice` reads its own lines that way, and a line can set
its own `tempo`. The voice is matched to the owner's reference by measurement (about 290 wpm, a median of about
200 Hz), never cloned from it (note 18).

`synth` writes <dir>/<line id>.wav (24 kHz mono, already sped up) and <dir>/voice.json: for every line its
length, the speech onset and end, and when each caption chunk starts and ends, from Kokoro's own word
timestamps divided by the rate.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

import numpy as np

SR = 24000
NARRATOR = {"voice": "am_adam", "tempo": 1.03, "rate": 1.45}


def with_phonemes(text: str, phonemes: dict) -> str:
    for w, ph in phonemes.items():
        text = re.sub(rf"\b{re.escape(w)}\b", f"[{w}](/{ph}/)", text)
    return text


def spoken(line: dict) -> str:
    return " ".join(sp for _, sp in line["chunks"] if sp).strip()


def norm(t: str) -> str:
    return re.sub(r"[^a-z0-9]", "", t.lower())


def chunk_times(line: dict, tokens: list[tuple[str, float, float]]) -> list[list[float]]:
    """Each chunk's (start, end), matching the chunk's spoken words to Kokoro's tokens by their letters."""
    out, k = [], 0
    toks = [(norm(t), a, b) for t, a, b in tokens if norm(t)]
    for _, sp in line["chunks"]:
        want = norm(sp)
        got, start, end = "", None, None
        while k < len(toks) and len(got) < len(want):
            t, a, b = toks[k]
            got += t
            start = a if start is None else start
            end = b
            k += 1
        if got != want:
            raise SystemExit(f"{line['id']}: chunk {sp!r} doesn't match the tokens ({got!r})")
        out.append([round(start, 3), round(end, 3)])
    return out


def speed_up(x: np.ndarray, rate: float) -> np.ndarray:
    """Play x `rate` times faster at the same sample rate (tempo and pitch both go up), band-limited by FFT."""
    if abs(rate - 1) < 1e-6:
        return x
    n = int(round(len(x) / rate))
    X = np.fft.rfft(x)
    return np.fft.irfft(X[: n // 2 + 1], n) * (n / len(x))


def voice_for(story: dict, who: str) -> dict:
    v = dict(NARRATOR)
    v.update(story.get("voice", {}))
    if who != "narrator":
        v.update(story.get("cast", {}).get(who, {}).get("voice", {}))
    return v


def synth(story_dir: Path, out: Path, only: list[str] | None = None) -> None:
    import soundfile as sf
    from kokoro import KPipeline

    story = json.loads((story_dir / "story.json").read_text())
    phon = story.get("phonemes", {})
    pipes = {}
    out.mkdir(parents=True, exist_ok=True)
    nv = voice_for(story, "narrator")
    meta = {"voice": nv["voice"], "tempo": nv["tempo"], "rate": nv["rate"], "sr": SR,
            "model": "hexgrad/Kokoro-82M (Apache 2.0)", "lines": {}}
    if only and (out / "voice.json").exists():
        meta["lines"] = json.loads((out / "voice.json").read_text())["lines"]
    for line in story["lines"]:
        if "pause" in line or (only and line["id"] not in only):
            continue
        v = voice_for(story, line.get("who", "narrator"))
        lang = "b" if v["voice"][0] == "b" else "a"
        pipe = pipes.setdefault(lang, KPipeline(lang_code=lang))
        text = spoken(line)
        tempo = v["tempo"] * float(line.get("tempo", 1.0))
        t0 = time.time()
        audio, tokens, off = [], [], 0.0
        for res in pipe(with_phonemes(text, phon), voice=v["voice"], speed=tempo):
            a = res.audio.numpy()
            for tk in res.tokens or []:
                if tk.start_ts is not None:
                    tokens.append((tk.text, off + tk.start_ts, off + tk.end_ts))
            audio.append(a)
            off += len(a) / SR
        y = speed_up(np.concatenate(audio).astype(np.float64), v["rate"]).astype(np.float32)
        sf.write(out / f"{line['id']}.wav", y, SR)
        ct = [[a / v["rate"], b / v["rate"]] for a, b in chunk_times(line, tokens)]
        ct = [[round(a, 3), round(b, 3)] for a, b in ct]
        meta["lines"][line["id"]] = {"text": text, "who": line.get("who", "narrator"), "voice": v["voice"],
                                     "rate": v["rate"], "tempo": tempo, "dur": round(len(y) / SR, 3),
                                     "onset": ct[0][0], "end": ct[-1][1], "chunks": ct}
        words = len(text.split())
        print(f"{line['id']}: {len(y) / SR:.2f}s ({words / max(1e-3, ct[-1][1] - ct[0][0]) * 60:.0f} wpm) "
              f"in {time.time() - t0:.1f}s  {text}", flush=True)
    (out / "voice.json").write_text(json.dumps(meta, indent=1))


def asr(wav: Path, timeline: Path) -> int:
    """Transcribe the narration and list every word Whisper heard differently from the script."""
    import difflib
    import subprocess

    from faster_whisper import WhisperModel

    tl = json.loads(timeline.read_text())
    want = " ".join(tl["lines"][l]["text"] for l in tl["order"] if "text" in tl["lines"][l])
    pcm = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(wav), "-ac", "1", "-ar", "16000", "-f", "f32le",
                          "-"], capture_output=True, check=True).stdout
    m = WhisperModel("small.en", device="cpu", compute_type="int8", cpu_threads=2)
    segs, _ = m.transcribe(np.frombuffer(pcm, np.float32), beam_size=5, language="en")
    heard = " ".join(s.text for s in segs)
    num = {str(i): w for i, w in enumerate("zero one two three four five six seven eight nine ten".split())}
    words = lambda t: [num.get(w, w) for w in re.sub(r"[^a-z0-9' ]", " ", t.lower().replace("-", " ")).split()]
    a, b = words(want), words(heard)
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    print(f"script {len(a)} words, heard {len(b)}, match {sm.ratio():.3f}")
    print("heard:", heard.strip())
    bad = 0
    for op, a1, a2, b1, b2 in sm.get_opcodes():
        if op == "equal":
            continue
        sa, sb = " ".join(a[a1:a2]), " ".join(b[b1:b2])
        if op == "insert" and a1 == len(a) and os.environ.get("BLOCKY_ASR_TAIL"):   # opt-in (ep23): after the last line
            print(f"  tail: Whisper repeated the end, ignored: {sb!r} (the film has no words there)")
            continue
        if same_spoken(sa, sb):
            print(f"  spelling: script {sa!r} | heard {sb!r} (the same words, spelled another way)")
            continue
        bad += 1
        print(f"  {op}: script {sa!r} | heard {sb!r}")
    print(f"{bad} word(s) heard wrong")
    return bad


SPELLINGS = {"grey": "gray", "colour": "color", "favourite": "favorite"}   # British and American spellings
# homophones: the same sound, and Whisper picks the spelling from the words around it ("under the bulb threw"), so
# hearing one for the other isn't a mispronunciation. `asr` lists them as spellings, never silently
# homophone pairs added by stories: creak/creek and shone/shown (ep16), hall/haul and ladder/latter, flapped
# (ep17), Wren said "ren" (ep20)
HOMOPHONES = {"threw": "through", "creek": "creak", "shown": "shone", "haul": "hall", "latter": "ladder",
              "wren": "ren", "wrens": "rens"}
NUMBERS = dict(enumerate(("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
                          "fifteen sixteen seventeen eighteen nineteen twenty").split()))


def _under100(n: int) -> str:
    tens = {2: "twenty", 3: "thirty", 4: "forty", 5: "fifty", 6: "sixty", 7: "seventy", 8: "eighty", 9: "ninety"}
    if n in NUMBERS:
        return NUMBERS[n]
    return tens[n // 10] + (NUMBERS[n % 10] if n % 10 else "")


def same_spoken(script: str, heard: str) -> bool:
    """True when two transcripts differ only in spelling: a spacing ("hand print"), an apostrophe
    ("mannequins"), a British spelling ("gray"), digits ("11") or a homophone ("threw" for "through"). Whisper
    writes what it hears its own way, so these aren't mispronunciations."""
    def canon(t):
        out = []
        for w in t.split():
            w = w.replace("'", "")
            w = NUMBERS.get(int(w), w) if w.isdigit() and int(w) in NUMBERS else w
            if w.isdigit() and 100 <= int(w) < 1000:   # "112" as "a hundred and twelve" (ep14)
                h, r = divmod(int(w), 100)
                w = ("a" if h == 1 else NUMBERS.get(h, str(h))) + "hundred" + ("and" + _under100(r) if r else "")
            w = SPELLINGS.get(w, w)
            out.append(HOMOPHONES.get(w, w))
        return "".join(out)
    return bool(script or heard) and canon(script) == canon(heard)


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["synth", "asr"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--only", default=None)
    ap.add_argument("--out", type=Path, default=Path("vo"))
    a = ap.parse_args()
    if a.cmd == "synth":
        synth(Path(a.args[0]), a.out, a.only.split(",") if a.only else None)
    else:
        sys.exit(1 if asr(Path(a.args[0]), Path(a.args[1])) else 0)
