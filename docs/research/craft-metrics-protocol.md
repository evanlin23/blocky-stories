# Browser protocol: craft metrics on 20 blocky Shorts (2026-11-03)

For the owner's browser extension. It measures the macro craft metrics (`craft-metrics.md`) on 17 fast-rising blocky
Shorts plus 3 of ours, in the browser while each one plays once. Nothing is downloaded. The 3 of ours calibrate the
browser numbers against `scripts/measure.py` on the same films, so the hits' numbers and ours compare like for like.

## Keep it light (the last study hit YouTube's bot check)
- **20 videos at most**, one tab, normal playback at 1x, each played through once. No seeking, no reloads, no
  comment scrolling, no channel pages.
- **Wait at least 20 s between videos**, and take a 2-minute break after video 10.
- **Stop at the first "Sign in to confirm you're not a bot"** (or any captcha or "unusual traffic" page). Report what's
  done so far. Never try to get past it.
- The script only reads the playing video into a 108 × 192 canvas 4 times a second. It never fetches anything.

## The 20 videos
From `docs/trends/deep/2026-11-03.md` (the 40 fastest): the story-length ones (90 s and up) across channels, plus ours.

| # | Video | Why |
|---|---|---|
| 1 | https://youtube.com/shorts/GXTY-HM3EBw | #1, town rule, 4.9M/day |
| 2 | https://youtube.com/shorts/J0OQXSo1chk | #2, warning title |
| 3 | https://youtube.com/shorts/2aucEdPHl9U | #3 |
| 4 | https://youtube.com/shorts/RVszt4A-ucc | #4, creepy |
| 5 | https://youtube.com/shorts/DY87dhwHDwA | #6, rule premise |
| 6 | https://youtube.com/shorts/sG4Wyz0V88k | #8, riddle, 179K-sub channel |
| 7 | https://youtube.com/shorts/pvZmPiEi-lA | #13, what-if world |
| 8 | https://youtube.com/shorts/cbfeTVzc-oQ | #15, creepy |
| 9 | https://youtube.com/shorts/tR5PnlH0jBo | #16, 51K-sub channel |
| 10 | https://youtube.com/shorts/im13Kmy6CVY | #17, rule world |
| 11 | https://youtube.com/shorts/E1aVuz1DKk8 | #19, 19K-sub channel |
| 12 | https://youtube.com/shorts/BVzb_90WD5A | #22, town rule |
| 13 | https://youtube.com/shorts/EG3e6rm_xi0 | #27, creepy character |
| 14 | https://youtube.com/shorts/uWQ0BRW6Kzw | #29, warning title, horror |
| 15 | https://youtube.com/shorts/0coSArNSisg | #31, 129-day-old channel |
| 16 | https://youtube.com/shorts/XqeykPf5_0U | #36, 88K-sub channel |
| 17 | https://youtube.com/shorts/HXKdYUU24hw | #37, creepy |
| 18 | https://youtube.com/shorts/n9GkKQGGYx8 | ours: back-row (our hit, 82.6% viewed) |
| 19 | https://youtube.com/shorts/2VLjg2AplBo | ours: ep38 drive-in (flop, 61.3%) |
| 20 | https://youtube.com/shorts/nKFNJT5MuFo | ours: knock-back (flop, 63.1%) |

Do 18 to 20 first. They're the calibration, and back-row is the one final we can't measure from a file.

## For each video
1. Open it, let it start, and click once on the page so it plays with sound. Run the script below **before 1 s has
   played** (or press the left arrow back to 0 once; that's the only seek allowed).
2. While it plays, fill in the eye-and-ear notes below. The script stops on its own when the Short loops or ends,
   and prints one JSON line.
3. Copy the JSON line, add the notes to it as the `"eye"` object, and move on after 20 s.

### The script (paste into the page console or run it as the extension's JavaScript)
```js
(() => {
  const v = [...document.querySelectorAll('video')].find(e => !e.paused && e.readyState >= 2) || document.querySelector('video');
  const W = 108, H = 192, cv = document.createElement('canvas'); cv.width = W; cv.height = H;
  const cx = cv.getContext('2d', { willReadFrequently: true });
  const S = []; let last = -1, err = null;
  const grid = d => { const g = new Float32Array(32 * 18);
    for (let r = 0; r < 32; r++) for (let q = 0; q < 18; q++) { let s = 0;
      for (let y = 0; y < 6; y++) for (let k = 0; k < 6; k++) { const i = ((r * 6 + y) * W + q * 6 + k) * 4;
        s += 0.2126 * d[i] + 0.7152 * d[i + 1] + 0.0722 * d[i + 2]; }
      g[r * 18 + q] = s / 36 / 255; } return g; };
  const sample = () => {
    const t = v.currentTime;
    if (S.length > 8 && (v.ended || t < last - 1)) return finish();          // looped or ended
    if (t === last) return;                                                 // paused or stalled: skip
    last = t;
    try { cx.drawImage(v, 0, 0, W, H); } catch (e) { err = String(e); return finish(); }
    const d = cx.getImageData(0, 0, W, H).data; let sl = 0, sl2 = 0, ss = 0, ns = 0;
    for (let i = 0; i < d.length; i += 4) { const r = d[i] / 255, g = d[i + 1] / 255, b = d[i + 2] / 255;
      const y = 0.2126 * r + 0.7152 * g + 0.0722 * b, mx = Math.max(r, g, b), mn = Math.min(r, g, b);
      sl += y; sl2 += y * y; if (mx > 0.04) { ss += (mx - mn) / mx; ns++; } }
    const n = d.length / 4, m = sl / n;
    S.push({ t, y: m, sd: Math.sqrt(Math.max(0, sl2 / n - m * m)), sat: ns ? ss / ns : 0, g: grid(d) });
  };
  const diff = (a, b) => { let s = 0; for (let i = 0; i < a.length; i++) s += Math.abs(a[i] - b[i]); return s / a.length; };
  const timer = setInterval(sample, 250);
  function finish() {
    clearInterval(timer);
    const dur = S.length ? S[S.length - 1].t - S[0].t : 0, dq = [];
    for (let i = 1; i < S.length; i++) dq.push(diff(S[i].g, S[i - 1].g));
    let ch = 0, pairs = 0;
    for (let i = 2; i < S.length; i += 2) { pairs++; if (diff(S[i].g, S[i - 2].g) > 0.04) ch++; }
    let run = 0, best = 0; for (const x of dq) { run = x < 0.006 ? run + 1 : 0; best = Math.max(best, run); }
    let dips = 0; for (let i = 1; i < S.length; i++) if (S[i].y < 0.03 && S[i - 1].y >= 0.03) dips++;
    const mean = a => a.reduce((p, c) => p + c, 0) / Math.max(1, a.length), r3 = x => Math.round(x * 1000) / 1000;
    const out = { url: location.href.split('?')[0], title: document.title.replace(/ - YouTube$/, ''),
      samples: S.length, seconds: r3(dur), error: err,
      picture_changes_per_10s: r3(ch / Math.max(1e-9, pairs * 0.5) * 10),
      picture_changes_per_10s_q: r3(dq.filter(x => x > 0.04).length / Math.max(1e-9, dq.length * 0.25) * 10),
      motion_energy_q: r3(mean(dq) * 100), longest_still_q_s: r3(best * 0.25),
      brightness_mean: r3(mean(S.map(s => s.y))), brightness_first_3s: r3(mean(S.filter(s => s.t - S[0].t < 3).map(s => s.y))),
      dark_frame_share: r3(S.filter(s => s.y < 0.12).length / Math.max(1, S.length)),
      saturation_mean: r3(mean(S.map(s => s.sat))), contrast_mean: r3(mean(S.map(s => s.sd))), black_dips: dips };
    console.log('CRAFT ' + JSON.stringify(out)); window.__craft = out;
  }
})();
```
If it prints an `error` (a "tainted canvas" or security error), the picture numbers can't be read on that page. Keep
the eye notes, leave the picture numbers out, and say so.

### The eye-and-ear notes (by hand, while it plays)
Pause nothing. Glance at these moments: **0:01, then every 10% of the length** (10 checkpoints).
- `caption_checks`: at each checkpoint, is a caption on screen (1 or 0)? A list of 10.
- `caption_words`: the word count of the caption at each checkpoint where one shows.
- `caption_height`: the caption's letter height (a capital letter, top to bottom) as a fraction of the video height,
  estimated once (e.g. 0.04). Ours is 0.031 (a capital is about 60 px of 1920).
- `face_big_checks`: at each checkpoint, is a face wider than 1/5 of the frame (1 or 0)?
- `camera_moving_checks`: at each checkpoint, is the camera or zoom moving (1 or 0)?
- `transitions_30s`: in the first 30 s, the count of each: `cut` (hard cut), `punch` (a sudden zoom-in), `zoom`
  (a smooth push), `whip` (a fast pan or slide), `flash`, `black` (a dip or fade to black), `shake`, `other`.
- `sfx_30s` (by ear, first 30 s): the count of sound effects you'd notice as separate events (whoosh, hit, door,
  footsteps count as one per burst; music and voice don't count). If the sound doesn't play, null.
- `bed`: is there always some sound under the voice (music or room tone), or are there dead-silent gaps? `always`,
  `gaps` or `unsure`.
- `voice_over_bed`: is the voice clearly on top? `clear`, `close` or `buried`.
- `one_line`: one sentence on what makes it look polished or cheap.

## How to report back
Paste one line per video, in order, as a single message to the lead session (session_019n1tKHLkea725KWepZp2PU).
Each line is the script's JSON with your notes added under `"eye"`:
```
CRAFT {"url":"https://www.youtube.com/shorts/GXTY-HM3EBw", ...script numbers..., "eye":{"caption_checks":[1,1,1,0,1,1,1,1,1,1],"caption_words":[2,1,3,2,2,1,2,3,2],"caption_height":0.05,"face_big_checks":[1,0,1,1,0,1,1,0,1,1],"camera_moving_checks":[1,1,0,1,1,1,0,1,1,1],"transitions_30s":{"cut":14,"punch":6,"zoom":2,"whip":1,"flash":0,"black":0,"shake":1,"other":0},"sfx_30s":11,"bed":"always","voice_over_bed":"clear","one_line":"every cut lands on a whoosh"}}
```
End with one line: `DONE n of 20` (and `BOT CHECK at #k` if one appeared). The lead commits the lines as
`docs/research/craft-metrics-hits.jsonl`, and `craft-metrics.md` → "Targets" gets re-set from them.

## The paste-ready prompt (for the extension)
> Measure craft metrics on 20 YouTube Shorts, following `docs/research/craft-metrics-protocol.md` in
> evanlin23/blocky-stories (the script, the notes and the report format are there). Open each URL in the table in
> this tab, in the order 18, 19, 20, then 1 to 17. For each one: let it start with sound on, run the protocol's
> JavaScript in the page before 1 s has played, watch it through once at normal speed, and fill in the eye-and-ear
> notes at 0:01 and every 10% of the length. When the script prints its `CRAFT {...}` line, add your notes under
> `"eye"`. Wait at least 20 s between videos, and take a 2-minute break after the 10th. Don't seek (except back to
> 0:00 once), reload, open comments or open channel pages, and download nothing. If YouTube shows "Sign in to
> confirm you're not a bot", a captcha or any unusual-traffic page, stop right there and don't try to get around it.
> Reply with the CRAFT lines in order and then `DONE n of 20` (plus `BOT CHECK at #k` if it happened).
