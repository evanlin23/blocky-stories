"""Encoding and review: ffmpeg in and out, the loudness check on the finished file, a contact sheet
and a spectrogram."""

from __future__ import annotations

import json
import re
import subprocess
import wave
from pathlib import Path

import numpy as np

from blocky.synth import SR


class VideoPipe:
    """Raw RGB frames in, H.264 out. CRF 16 and tune=animation keep flat pixel areas clean."""

    def __init__(self, path: Path, w: int, h: int, fps: int, crf: int = 16, preset: str = "medium"):
        self.path = Path(path)
        self.proc = subprocess.Popen(
            ["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
             "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", preset, "-tune", "animation",
             "-crf", str(crf), "-pix_fmt", "yuv420p", "-g", str(fps * 2), "-an", str(self.path)],
            stdin=subprocess.PIPE)

    def write(self, rgb: np.ndarray) -> None:
        self.proc.stdin.write(np.ascontiguousarray(rgb, dtype=np.uint8).tobytes())

    def close(self) -> None:
        self.proc.stdin.close()
        if self.proc.wait() != 0:
            raise RuntimeError(f"ffmpeg failed writing {self.path}")


def write_wav(path: Path, audio: np.ndarray) -> None:
    """24-bit stereo PCM at SR."""
    a = np.clip(audio, -1.0, 1.0 - 2**-23)
    ints = np.round(a * 2**23).astype("<i4")
    raw = ints.view(np.uint8).reshape(-1, 4)[:, :3].tobytes()
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(3)
        w.setframerate(SR)
        w.writeframes(raw)


def read_wav(path: Path) -> np.ndarray:
    with wave.open(str(path)) as w:
        n, ch, sw = w.getnframes(), w.getnchannels(), w.getsampwidth()
        raw = np.frombuffer(w.readframes(n), dtype=np.uint8)
    if sw == 3:
        b = raw.reshape(-1, 3)
        ints = (b[:, 0].astype(np.int32) | (b[:, 1].astype(np.int32) << 8) | (b[:, 2].astype(np.int32) << 16))
        ints = np.where(ints >= 2**23, ints - 2**24, ints)
        return (ints / 2**23).reshape(-1, ch)
    return (np.frombuffer(raw.tobytes(), dtype="<i2") / 32768.0).reshape(-1, ch)


def mux(video: Path, wav: Path, out: Path) -> None:
    """Copy the video, encode the already-mastered audio to AAC (no loudnorm: master() set it)."""
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(video), "-i", str(wav),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
                    "-ar", str(SR), "-movflags", "+faststart", "-shortest", str(out)], check=True)


def ebur128(path: Path) -> dict:
    """Integrated loudness and true peak of a file, measured by ffmpeg's ebur128 filter."""
    res = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true",
                          "-f", "null", "-"], capture_output=True, text=True)
    s = res.stderr[res.stderr.rfind("Summary:"):]
    return {"lufs": float(re.search(r"I:\s+(-?[\d.]+) LUFS", s).group(1)),
            "true_peak_dbtp": float(re.search(r"True peak:\s+Peak:\s+(-?[\d.]+) dBFS", s).group(1))}


def probe(path: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate:format=duration", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True)
    j = json.loads(out.stdout)
    num, den = j["streams"][0]["r_frame_rate"].split("/")
    return {"w": j["streams"][0]["width"], "h": j["streams"][0]["height"], "fps": int(num) / int(den),
            "duration": float(j["format"]["duration"])}


def contact_sheet(frames: list[tuple[str, np.ndarray]], path: Path, cols: int = 5, thumb_w: int = 270) -> None:
    """A grid of labelled frames (RGB arrays at any size), scaled to thumb_w wide."""
    from PIL import Image, ImageDraw

    thumbs = []
    for label, rgb in frames:
        im = Image.fromarray(rgb)
        k = thumb_w / im.width
        thumbs.append((label, im.resize((thumb_w, int(im.height * k)), Image.NEAREST if k >= 1 else Image.BILINEAR)))
    th = thumbs[0][1].height
    rows = -(-len(thumbs) // cols)
    sheet = Image.new("RGB", (cols * (thumb_w + 6) + 6, rows * (th + 24) + 6), (24, 22, 28))
    d = ImageDraw.Draw(sheet)
    for i, (label, im) in enumerate(thumbs):
        x, y = 6 + (i % cols) * (thumb_w + 6), 6 + (i // cols) * (th + 24)
        sheet.paste(im, (x, y + 18))
        d.text((x, y + 2), label, fill=(230, 225, 215))
    sheet.save(path)


def spectrogram(audio: np.ndarray, path: Path, marks: list[tuple[float, str]] = (), title: str = "") -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    mono = audio.mean(axis=1) if audio.ndim == 2 else audio
    fig, ax = plt.subplots(figsize=(18, 6), dpi=90)
    ax.specgram(mono, NFFT=2048, Fs=SR, noverlap=1536, cmap="magma", vmin=-120)
    ax.set_yscale("symlog", linthresh=200)
    ax.set_ylim(30, 16000)
    ax.set_xlim(0, len(mono) / SR)
    ax.set_xlabel("seconds")
    ax.set_ylabel("Hz")
    for t, label in marks:
        ax.axvline(t, color="w", lw=0.6, alpha=0.8)
        ax.text(t + 0.08, 12000, label, color="w", fontsize=8, va="top", rotation=90)
    if title:
        ax.set_title(title)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
