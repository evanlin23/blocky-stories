# Reel watch notes 2: YouTube Shorts + audio (2026-11-02)

Round 2 of research for **Panda Nano Adventures**. It extends [2026-11-01-reel-watch-notes.md](2026-11-01-reel-watch-notes.md). No likes, follows, subscribes, comments or saves were made. YouTube's caption setting was switched back to Off after the session.

## How this was done (read first: "with sound")

I can't listen the way a person does. Instead, **each video's soundtrack was captured and analysed in the browser while it played at 1× speed**:
- **Spoken words (YouTube):** taken from YouTube's own auto-generated transcript, collected live as the Short played. These are **ASR text, not hand-checked**, so small mis-hearings are possible ("bow ring" for "bell rang"). On Instagram (no auto-transcript), words come from the burned-in captions, as in round 1.
- **Voice speed:** words ÷ duration from the transcript (YouTube) or captions (Instagram).
- **Voice pitch:** the median fundamental frequency (Hz) of voiced frames where the voice dominates the music. Rough guide: adult male ~100–150 Hz, adult female ~180–250 Hz, children ~250–300 Hz. Music can leak in, so treat it as ±15%. "Pitch spread" (semitone SD) shows how expressive vs. flat the read is.
- **One voice or several:** from distinct pitch clusters plus YouTube's speaker-change markers (">>") and dialogue in the transcript.
- **"AI or sped-up":** **cannot be confirmed without listening.** Where speed (>4.5 words/s), pitch and flatness point that way, it's flagged as an *inference*.
- **Music:** from a spectrogram and band levels: whether a bed runs under the voice, how loud the bass is relative to the voice, whether a steady beat exists, and **where the bed drops out** (near-silence ≥0.5 s). **Genre names are not given as fact.** YouTube's own "[music]" tags in the transcript corroborate the bed.
- **Sound effects:** sharp broadband hits detected in the audio, with timestamps. *What* each SFX is comes from the matching picture/script.
- Views/likes/comments were taken on 2026-11-01/02. "Top 5 comments" = the 5 most-liked among the ~50–100 loaded by default. Usernames containing slurs/offensive references are redacted.

### Which Shorts were picked (Part A)
- Searched YouTube with the **Shorts** filter for "roblox story", "in this world roblox", "roblox horror story" and "roblox animation story" (368 unique Shorts). I checked publish dates on the top 70 by views: 30 were posted since 2026-08-01.
- **The 12 highest-viewed story Shorts from the last 3 months**, from **8 channels**. Two 14–17 s non-story edits (luu_kki, Renz animation) were skipped.
- **Low-view contrast:** none of these 8 channels has a story Short **under 20K** views from the last 3 months that is older than 2 days. Only Gelo Stories' Short posted *today* was at 19K, which is too fresh to judge. So the 3 contrast picks are **the lowest-viewed eligible Shorts from the same channels (106K–299K)**, each 30–100× below its channel's hits.

## Part A at a glance (YouTube Shorts)

| # | Short | Channel | Posted | Views | Likes | Comments | Length | Tone | Rule visible by 2 s | Voice speed | Pitch |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Y1 | [Everyone can see your lies](https://www.youtube.com/shorts/tCxbrBltKHI) | ItsGuestCap | Aug 18 | 35.9M | 565K | 2,840 | 76 s | Emotional | Yes (numbers over heads) | 4.3 w/s | ~230–250 Hz |
| Y2 | [Rattina's Story](https://www.youtube.com/shorts/2l_gY9Jqv-4) | Jahrsel | Aug 3 | 22.9M | 199K | 2,431 | 21 s | Creepy/sad lore | n/a (monster at 2 s) | no voice | n/a |
| Y3 | [Saddest Story of Dr. Harlow](https://www.youtube.com/shorts/_4IFW78Zyac) | 순록 | Aug 14 | 19.4M | 274K | 4,368 | 31 s | Emotional lore | n/a | no voice | n/a |
| Y4 | [Everyone Is A Magnet](https://www.youtube.com/shorts/gSn70aSHsbs) | Gneef | Oct 17 | 18.9M | 377K | 3,091 | 96 s | Wonder → emotional | Yes (glowing wrists) | 4.4 | ~205–210 |
| Y5 | [One Word They Can't Say](https://www.youtube.com/shorts/eDDvBbSi3zk) | ItsGuestCap | Aug 2 | 18.0M | 325K | 2,566 | 72 s | Emotional | Yes (words over heads) | 4.6 | ~196–207 |
| Y6 | [You Have A Price](https://www.youtube.com/shorts/TsyAEsZ7zi0) | Gneef | Oct 16 | 17.1M | 408K | 1,471 | 77 s | Emotional | Yes (price tags) | 4.0 | ~200–205 |
| Y7 | [You're the animal...](https://www.youtube.com/shorts/VxnDoGeA1bs) | JohnnyBoyRBX | Aug 9 | 14.3M | 210K | 4,937 | 59 s | Creepy + fact | Hook visual (fangs) | 5.2 | ~180–210 |
| Y8 | [Everyone Has A Giant Version](https://www.youtube.com/shorts/9K1bOjMUj7E) | RealDanty | Oct 18 | 13.9M | 271K | 945 | 162 s | Creepy/dark fantasy | Yes (giants) | 4.3 | ~180 |
| Y9 | [Voice in their head](https://www.youtube.com/shorts/Y7IyM87DmrQ) | Ryex | Oct 25 | 12.8M | 378K | 3,870 | 145 s | Creepy → warm | Yes (blue orbs) | 4.9 | ~185 + ~280–350 (2 voices) |
| Y10 | [MOVING is deadly](https://www.youtube.com/shorts/HesZazDqE5M) | Ryex | Sep 15 | 11.1M | 171K | 1,670 | 54 s | Creepy | Yes (monster, skull) | 4.4 | ~233 |
| Y11 | [3 Steal Buttons](https://www.youtube.com/shorts/e67RuR5nQR0) | ItsGuestCap | Sep 14 | 9.8M | 147K | 521 | 67 s | Emotional | Yes (wrist buttons) | 4.8 | ~220–240 |
| Y12 | [Your Son Is Haunted](https://www.youtube.com/shorts/j1vrfEnEiI8) | Gelo Stories | Oct 12 | 9.6M | 335K | 694 | 120 s | Creepy → emotional | Yes (as action) | 3.9 | ~200 (+ child voice) |
| L1 | [Replay Any Memory](https://www.youtube.com/shorts/fp-F6vhgwOc) | ItsGuestCap | Oct 18 | 106K | ~2K | 26 | 55 s | Emotional, low stakes | Partly | 5.0 | ~216–230 |
| L2 | [TOUCH is deadly](https://www.youtube.com/shorts/9lp9G-glh6k) | Ryex | Sep 14 | 299K | 5.8K | 210 | 48 s | Creepy/peril | Generic skull only | 4.4 | ~285 |
| L3 | [WIND UP CREATURE](https://www.youtube.com/shorts/asxZdJwcJb4) | RealDanty | Oct 24 | 177K | hidden | 64 | 121 s | Creepy → heroic | No (dark, cameos) | 4.3 | ~190–205 |

## Part A: Short-by-Short notes


### Y1. In this world everyone can see your lies (HIT)
- **URL:** https://www.youtube.com/shorts/tCxbrBltKHI · **Channel:** ItsGuestCap (@itsguestreal) · **Posted:** 2026-08-18 · **Views:** 35.9M · **Likes:** 565K · **Comments:** 2,840 · **Length:** 76 s · 720p
- **First spoken line (YouTube auto-transcript):** "In this world, everyone can see how many times you've lied before."
- **First on-screen caption:** "In this WORLD" (2–6-word phrase blocks, white with a black outline, key words in CAPS, ~68% down). Title: "In this world everyone can see your lies #roblox #shorts"
- **First 2 seconds:** a classroom with a kid asleep face-down on a desk. Pull-back to rows of students; by 1.5 s **big numbers float over every student's head** (220, 345, 64…).
- **Rule visible by 2 s?** Yes. Lie-count numbers over heads at 1.5 s.
- **Premise:** Everyone's lifetime lie count floats over their head; Dylan (0 lies) judges everyone until he realises the kid with 1,528 lies takes the blame for others. → **Emotional** (a wonder-rule frame).
- **Beats:**
  - 0–14 s rule and examples: 29, 68, a teacher with 184; "A low number meant friends, trust, and respect".
  - 14–28 s protagonist: "Dylan's number was zero"; he starts "judging everyone by their number", even his dad (200).
  - 26–35 s antagonist: "Then there was Tyler. He had lied 1,528 times… Dylan even made fun of him… calling him the real-life Pinocchio".
  - 35–45 s turn: a phone is stolen and Tyler says "It was me." "But right then his number changed… The number only goes up when you lie. So why would Tyler lie about stealing a phone?"
  - 45–68 s reveal: Tyler's lies began at seven, taking the blame for his little brother's broken plate. "Every kid about to get in trouble reminded him of his little brother."
  - 68–76 s ending: "Tears filled Dylan's eyes… He looked at his number and saw a liar, but he never saw that one kid taking the fall for everyone else."
- **Twist:** The "worst liar" is the kindest kid, taking blame for others. Planted at 26–35 s (Tyler mocked) and by the number ticking up when he confesses (38 s). It flips the opening premise that high number = bad person.
- **Ending:** Bittersweet/moral. The last line reframes the rule; no question.
- **Tone:** Emotional. Not creepy.
- **Lore signals:** none in the video. **The creator pinned their own question:** "How many lies do you think your number would show?"
- **Audio:**
  - **Voice:** one narrator (third person), **~4.3 words/s (very fast)**. Measured voice pitch ≈ 230–250 Hz (high for an adult). A low peak at ~87 Hz is music bass, not voice. The speed plus high pitch is consistent with a TTS or sped-up voice, but that is an inference, not something I heard.
  - **Music:** continuous bed under the whole video (YouTube's transcript marks "[music]" 5 times). A heavier sustained bass note enters at ~28–30 s ("He had lied 1,528 times").
  - **Drop-outs:** short dips at ~7.5 s and **25.5–27.5 s**, a beat of near-silence right before Tyler's number is revealed.
  - **SFX:** broadband hits at 15.9 s, 24.8 s and 27.3 s (reveal stings).
  - Loudness: median −17 dBFS (loud, compressed).
- **Captions:** phrase blocks (2–6 words), white, black outline, key words CAPS ("WORLD", "MANY", "TIMES"), lower-middle of frame.
- **Look:** blocky Roblox avatars in a bright classroom/home/school-yard; numbers in big 3D digits over heads. **Frequent white flash-wipe transitions** (overexposed frames between scenes). About 50 cuts in 76 s (one every ~1.5 s).
- **Top 5 comments (by likes, ~100 loaded):**
  1. @yv2990 (16K): "Teacher - 186 / Student - Sir Did i pass ?  / Teacher - Yes you did / Teacher - 187"
  2. @Itsguestreal (3.7K, creator): "How many lies do you think your number would show?"
  3. @Rip_GaigeMeng-o4d (1.5K): "How do those kids have such small amouts of lies"
  4. @Dedu_yt1890 (1.2K): "People with 1000+ lies doesn't mean that person a bad person(Some are bad too but some are good this what i meant) / Edit: Guys TYSM i got so many likes yay"
  5. @gatos1202 (745): "Sometimes lying can be good..."
  - **Latch onto:** jokes using the rule (the teacher's count ticking up), the creator's "what would yours be" prompt, debating the moral, nitpicking the numbers.

### Y2. Rattina's Story ("I'm Not A Monster – Part 1") (HIT)
- **URL:** https://www.youtube.com/shorts/2l_gY9Jqv-4 · **Channel:** Jahrsel · **Posted:** 2026-08-03 · **Views:** 22.9M · **Likes:** 199K · **Comments:** 2,431 · **Length:** 21 s · 720p
- **First spoken line:** none. **No narration** (YouTube found no speech to auto-transcribe; the audio is music only).
- **First on-screen caption:** a fixed title card at the top, "I'm Not A Monster / Part 1", for the whole video. Title: "Rattina's Story #animalhospital #roblox #animalhospitalroblox…"
- **First 2 seconds:** a yellow cartoon cat (a character from the Roblox game *Animal Hospital*) lies sedated on a blue hospital bed; a syringe of green liquid goes in; at 2.0 s her mouth splits into a huge red fanged monster mouth.
- **Rule visible by 2 s?** No "rule". It's a lore/transformation piece; the monster reveal is at 2 s.
- **Premise:** A wordless origin story for a game character: experiments turn a patient into a "monster". → **Creepy/sad lore** (fan animation of an existing Roblox game).
- **Beats (visual only):** 0–2.4 s injection and monster mouth → 3.9–8.4 s masked doctors, another patient caged → 10–16 s a black cat character behind bars, a tablet showing a smiling face, a flash/glitch → 16–21 s the black cat walks a dark hallway and ends on a giant grinning black-cat close-up.
- **Twist:** visual reveal that the "monster" was made by the hospital (comments confirm it as game lore: "So that's why ratthew always goes to room6 and 8").
- **Ending:** ominous cliffhanger; explicitly "Part 1".
- **Tone:** Creepy/sad. No speech, so no explicit warm beat.
- **Lore signals:** strong. A "Part 1" series label; built on an existing game's characters and rooms; commenters connect it to in-game lore and hope the devs "approve" it.
- **Audio:**
  - **Voice:** none.
  - **Music:** a single melodic track (dense harmonic stacks = a song/instrumental with melody), bass-heavy (bass about 6 dB *above* the voice band), loud (median −16 dBFS).
  - **Drop-outs:** one brief dip at ~1.4–1.9 s just before the monster-mouth reveal.
  - **SFX:** hits at 0.4 s, 5.2 s, 6.5 s, 15.6 s (the injection, the cage, the glitch).
- **Captions:** none besides the fixed title card.
- **Look:** custom smooth cartoon animal characters (not blocky R6 avatars) in hospital sets, mostly dark blue/black. About 18 cuts in 21 s (one every ~1.2 s).
- **Top 5 comments (~100 loaded):**
  1. @TahaAyoub-x4g (1.2K): "Making new faces for this animation is amazing🥹️"
  2. @Mina_dordevic (866): "So that's why ratthew always goes to room6 and 8"
  3. @AllieEvans-o7e (304): "The developers might acually approve this of what happend due to the lore! Wow!"
  4. @CurtMelbourneDumalanta (231): ""Being small has its advantages" and it's disadvantages"
  5. @dupea123 (158): "THIS IS AMAZING BROO"
  - **Latch onto:** game lore theories, animation craft (new faces), hype.

### Y3. The Saddest Story of Dr. Harlow [Animal Hospital animation] (HIT)
- **URL:** https://www.youtube.com/shorts/_4IFW78Zyac · **Channel:** 순록 (Korean-named creator) · **Posted:** 2026-08-14 · **Views:** 19.4M · **Likes:** 274K · **Comments:** 4,368 · **Length:** 31 s · 720p
- **First spoken line:** none. **No narration, no captions** (YouTube found no speech).
- **First on-screen text:** none (watermark only). Title: "The Saddest Story of Dr. Harlow [Animal Hospital animation]".
- **First 2 seconds:** a flat 2D cartoon family picnic: a deer dad, a rabbit mom and a small child, laughing on a log. At 1.8 s a brown bear with a camera takes their photo.
- **Rule visible by 2 s?** No rule; a happy-family setup.
- **Premise:** A wordless backstory for *Animal Hospital*'s villain doctor: a happy family, then loss, then he's forced to make "anomalies". → **Emotional/sad lore.**
- **Beats (visual):**
  - 0–6 s happy family photo.
  - 6 s white flash.
  - 8–10 s Dr. Harlow in his lab coat with a tray.
  - 10–16 s the child as a patient on a hospital/X-ray screen; a drawing of the child.
  - 16–22 s a dark lab and a heartbeat monitor.
  - 22–27 s a corporate logo on a red screen; Harlow injected (big green syringe).
  - 28–31 s he's left at a window.
- **Twist:** the villain was a grieving father forced by the corporation (viewers spell it out in the comments).
- **Ending:** sad and open.
- **Tone:** Emotional (sad).
- **Lore signals:** very strong. The whole piece is fan lore for an existing Roblox game; comments write long lore explanations.
- **Audio:**
  - **Voice:** none (the detected "pitch" is a melody line, not speech).
  - **Music:** 0–10 s a full, bass-heavy upbeat track. **At 10.0 s the music switches abruptly**: the bass drops out and a single slow melodic line (piano/music-box-like) carries the rest, i.e. **a happy-to-sad music switch exactly at the turn**. A small hit at 18.4 s.
  - **Drop-outs:** the bass bed drops at 10 s and doesn't return.
- **Captions:** none.
- **Look:** flat 2D cartoon (hand-drawn style, not Roblox 3D), soft greens, then dark grey/red. About 16 cuts in 31 s (~1.9 s).
- **Top 5 comments (~100 loaded):**
  1. @Legotactical-q8t (844): "It’s not Harlow’s fault it’s the animal corporation’s fault"
  2. @GaelKings777 (300): "I hadn't seen anything so profound since 99 Nights in the Forest."
  3. @jgmene (176): "So if you don’t know, Dr. Harlow is actually good. His wife died and his child became an a anomaly and it’s the animal corporation‘s fault because they made the first anomaly ever and also she or he turned Dr. Hollow into a anomaly  forever and forced him to make anomaly’s forever so it’s not his fault. He’s actually good it’s the animal corporation‘s fault…"
  4. @Oliver-o-u7m (171): "He's actually a good person. But he's been given an evil potion forever. And that's why he's always creating evil anomalies."
  5. @Pomnislayqueen (164): "If that actually happened, and this was the real lore behind his family I WOULD AVENGE HIM!"
  - **Latch onto:** lore explanation, sympathy for the villain, comparisons to other Roblox games.

### Y4. In This World, Everyone Is A Magnet 🧲 (HIT)
- **URL:** https://www.youtube.com/shorts/gSn70aSHsbs · **Channel:** Gneef (same creator as Instagram @gneef.original) · **Posted:** 2026-10-17 · **Views:** 18.9M · **Likes:** 377K · **Comments:** 3,091 · **Length:** 96 s · 720p
- **First spoken line (auto-transcript):** "In this world, every person is born a magnet, red or blue."
- **First on-screen caption:** "in" (single words, white, black outline, ~66% down).
- **First 2 seconds:** a sunny suburban street with a school bus. Two kids, one with **glowing red** and one with **glowing blue** wrists/arms, walk toward the camera.
- **Rule visible by 2 s?** Yes. Coloured glowing wrists from frame 0.
- **Premise:** Everyone is a red or blue magnet (opposites stick, same colours repel); a red kid with an all-red family has never been hugged. → **Wonder rule, emotional payoff.**
- **Beats:**
  - 0–20 s rule plus 4 gags: married couples "glued at the hip"; "Date night is just two people walking sideways"; "Two reds shaking hands is how you get thrown through a window"; bus seating red-blue-red-blue.
  - 20–26 s wound: "I'm red, so is my mom, so is my dad. My whole life, nobody in my house has ever hugged me."
  - 26–33 s setup: Theo (blue) always tries to sit next to him and he always moves away.
  - 33–45 s inciting: the frozen lake; "grownups… too heavy for the ice"; a girl falls through.
  - 45–60 s plan: "Line up, red, blue, red, blue"; a human chain, "click, click, click".
  - 60–67 s turn: "Her wrist was glowing red. She was red, like me. If I grabbed her, she'd shoot right under the ice."
  - 67–78 s twist: "Theo! … Climb over me." Theo grabs her: "A blue and a red, stuck. Pull!"
  - 80–96 s emotional payoff: dad stops "two feet away, like always", so he pulls Theo in between them: "Red, blue, red. Click, click. And for the first time in my life, my dad hugged me, with Theo squished right in the middle, and none of us let go."
- **Twist:** The same-colour problem blocks the rescue, and the kid he kept avoiding (Theo) is the solution. Planted at 26–33 s. The ending uses Theo to solve the opening wound (no hugs).
- **Ending:** Happy and warm. It loops back to "nobody has ever hugged me".
- **Tone:** Wonder/comedy opening, then **emotional**. Not creepy (mild peril).
- **Lore signals:** none. Commenters flag a plot hole ("How were his parent's 2 reds!?").
- **Audio:**
  - **Voice:** one first-person kid narrator plus shouted lines ("Theo!", "Pull!"), **~4.4 words/s (very fast)**. Measured voice pitch ≈ 205–210 Hz (medium-high).
  - **Music:** bed throughout (YouTube's transcript marks "[music]" ~10 times). A **sustained bass/drone enters at ~25 s exactly on "nobody in my house has ever hugged me"** and stays heavier for the rest.
  - **Drop-outs:** short dips at 9.5 s, 12 s and 23 s (gaps between gag lines).
  - **SFX:** hits at 13.1 s (thrown through a window), 50.6 s (chain "click") and 76.3 s ("Click", the girl grabbed). The "click" sounds are written into the narration.
  - Loudness median −18.7 dBFS.
- **Captions:** single word, white with a black outline, ~66% down.
- **Look:** classic Roblox R6 avatars with glowing coloured limbs. Sunny suburb, school, then a snowy forest lake. About 47 cuts in 96 s (one every ~2 s).
- **Top 5 comments (~100 loaded):**
  1. @mr.electric39140 (13K): "How were his parent's 2 reds!?"
  2. @ROBIN-ON-PAWS-u5z (5.2K): "Two people in my friends neighborhood are killing black cats on Halloween and now she has to hide her cats every year and it’s just sickening and cruel please stop this" (off-topic)
  3. @FantasyTank123 (4.5K): ""Every married couple is one red and one blue"          "I'm red, so is my mom, so is my dad""
  4. @SylviasWatch (2.3K): "Wait a sec if couples are red and blue THEN WHY ARE YOURS BOTH RED!?!?!! *edit) WOAH 2.3K LIKES!?!?! THANK YOU THATS THE MOST IVE EVER GOTEN"
  5. @SSD_7473 (797): ""And kids , that's how I met your other father""
  - **Latch onto:** **the plot hole** (3 of the top 5), jokes reading the ending as romance.

### Y5. In This World… Everyone Is Born With One Word They Can't Say (HIT)
- **URL:** https://www.youtube.com/shorts/eDDvBbSi3zk · **Channel:** ItsGuestCap · **Posted:** 2026-08-02 · **Views:** 18.0M · **Likes:** 325K · **Comments:** 2,566 · **Length:** 72 s · 720p
- **First spoken line (auto-transcript):** "In this world, everyone is born with one word above their head. And if you ever say your own word, you disappear forever."
- **First on-screen caption:** "In this WORLD" (phrase blocks, white with a black outline, CAPS key words). The word over each head is in red letters.
- **First 2 seconds:** a close-up of a classic red-cap Roblox avatar, then a playground crowd; by 2 s **red words float over every head** ("KEYS", "WINTER", "MIRROR").
- **Rule visible by 2 s?** Yes. Words over heads at 1.5–2 s.
- **Premise:** Your forbidden word floats above you, and Ryan's word is "help". → **Emotional.**
- **Beats:**
  - 0–11 s rule and gags: "One kid's word was banana. He just pointed at it whenever he wanted one. Another kid's word was Emma. He just called her his sister."
  - 11–30 s problem: "Ryan's word was help"; stuck on a test, he can't ask; "he held it in and faced it alone."
  - 30–48 s turn: "living without help also changed Ryan. He could always tell when someone needed help"; he helps a lost boy and a crying kid. "But when Ryan needed someone, he was always alone."
  - 48–62 s payoff: crying behind the school, he hears footsteps; the people he helped come one by one (ice cream, sitting beside him).
  - 62–72 s moral: "the people who truly care about you will never wait for you to ask for…" (**the video cuts off before the word "help"**).
- **Twist:** No plot twist. It's an emotional reframe of the rule ("His word was never there to keep help away"). The final unspoken "help" is a clever audio/structure payoff of the rule.
- **Ending:** Warm/bittersweet. The last line deliberately withholds the forbidden word (loop to the rule).
- **Tone:** Emotional. Not creepy.
- **Lore signals:** none.
- **Audio:**
  - **Voice:** one third-person narrator, **~4.6 words/s (very fast)**. Measured voice pitch ≈ 196–207 Hz (a low peak at 87 Hz is music bass). Consistent with the same voice as Y1 (same channel).
  - **Music:** bed throughout ("[music]" tags ~10). **A 2-second near-silent drop at 30.5–32.5 s** (right as the story turns: "Little by little, Ryan stopped believing anyone would ever help him"), after which a **sustained bass drone enters and stays** to the end.
  - **SFX:** one hit at 16.3 s.
  - Loudness median −17.5 dBFS.
- **Captions:** phrase blocks, white, black outline, CAPS key words; red words over heads as diegetic text.
- **Look:** blocky Roblox avatars (classic red-cap "Builderman"-style, camo jackets), school/store/playground sets, bright. White flash transitions. About 48 cuts in 72 s (one every ~1.5 s).
- **Top 5 comments (~100 loaded):**
  1. @Luckai26 (1.6K): "or maybe Ryan should just say "I would require aid pls" /  / "Edit, oh my gauwd so many wikes thank youw" ahh"
  2. @Rati079 (1.5K): ""thank you guys for he-" gets eradicated"
  3. @AYLA-d5c5t (770): "my dumb ahh waiting for the real footage"
  4. @ZKloo (691): "There's a thing called "Save me""
  5. @JubiDaCwazee (568): "When someone thinks I’ll judge them for being emotional but i genuinely cry to all these videos"
  - **Latch onto:** loopholes (synonyms for help), jokes about him accidentally saying it, admitting they cry.

### Y6. In This World, You Have A Price 💸 (HIT)
- **URL:** https://www.youtube.com/shorts/TsyAEsZ7zi0 · **Channel:** Gneef · **Posted:** 2026-10-16 · **Views:** 17.1M · **Likes:** 408K · **Comments:** 1,471 · **Length:** 77 s · 720p
- **First spoken line (auto-transcript):** "In this town, everyone has a price tag above their head." (The title says "world"; the narration says "town".)
- **First on-screen caption:** "in" (single words, white with a black outline, ~66% down).
- **First 2 seconds:** a sunny suburban street; townspeople walk with **white price-tag bubbles over their heads** ("$410,000", "$90,000", "$3,600,000").
- **Rule visible by 2 s?** Yes, from 0.5 s.
- **Premise:** Anyone who pays your price owns you, and price = how many people care about you; Grandma is worth $5 and a man plans to buy her. → **Emotional**, with mild threat.
- **Beats:**
  - 0–10 s rule plus gags: "Moms are worth millions. Babies are priceless. Lonely people? They're cheap."
  - 10–20 s wound: "my grandma is the loneliest person in town… nobody visits her except me. Her tag says $5."
  - 20–26 s villain and deadline: Mr. Puff wants her house; "I get paid on Friday… See you then, ma'am." "I had five days to make the whole town care about my grandma."
  - 27–39 s escalation (x3, a countdown): Monday cookies $20 → Tuesday dance moves $60 → Wednesday library stories $90. "It wasn't enough."
  - 39–48 s low point: Friday, "$200." Grandma's tag says $95; "It's okay, sweetie."
  - 48–63 s twist: "Footsteps. Hundreds of them." The class, the team, the library kids and their parents arrive; the tag jumps $500 → $5,000 → … → $50,000,000.
  - 63–77 s ending: "her tag stopped. It said priceless… Mr. Puff… walked away, alone. And my grandma? She will never be alone again."
- **Twist:** The town shows up, and her price becomes "priceless", which echoes "Babies are priceless" (planted at 6 s). The villain leaves "alone", a mirror reversal.
- **Ending:** Happy/warm. The last line answers the opening ("Lonely people… cheap").
- **Tone:** Emotional. Not creepy.
- **Lore signals:** a commenter recognises a character ("I didn't realized that was bart"), suggesting recurring cast members across Gneef videos.
- **Audio:**
  - **Voice:** one first-person kid narrator plus character lines (Mr. Puff, Grandma), **~4.0 words/s (fast)**. Pitch ≈ 200–205 Hz.
  - **Music:** bed throughout ("[music]" tags ~8). **A sustained bass/drone enters at ~25 s** ("I had five days…"), the same placement as Gneef's Magnet Short. Strongest beat regularity of the set so far (a steady pulse ~70 BPM).
  - **Drop-outs:** none beyond a short gap at 7.5 s.
  - **SFX:** hits at 0.9 s (opening whoosh) and 59.0 s (the tag jumping to millions).
  - Loudness median −19 dBFS.
- **Captions:** single word, white with a black outline.
- **Look:** classic Roblox R6 avatars (yellow-skin "noob" style, a grandma with white hair); price-tag UI bubbles over heads. Sunny suburb, school, library, porch. About 49 cuts in 77 s (one every ~1.6 s).
- **Top 5 comments (~100 loaded):**
  1. @PhotoNegativeMickey-u3b (16K): "Why not buy Mr puff"
  2. @I_am_bread_becouse_i_am_bread (12K): "Just buy the 12 dollar guy"
  3. @NanaA-v7i (4.3K): "I didn't realized that was bart"
  4. @DalaKeichour (2.5K): "Why not buy your grandma?"
  5. @Gametopia551 (1.4K): "That’s something called slavery and it existed up until the 1880s"
  - **Latch onto:** **loophole solutions** (buy Mr. Puff or Grandma), recognising a character, real-world commentary.

### Y7. You're the animal... (HIT)
- **URL:** https://www.youtube.com/shorts/VxnDoGeA1bs · **Channel:** JohnnyBoyRBX · **Posted:** 2026-08-09 · **Views:** 14.3M · **Likes:** 210K · **Comments:** 4,937 · **Length:** 59 s · 720p
- **First spoken line (auto-transcript):** "You wake up and feel your teeth growing sharper, but you don't see anything wrong when you check the mirror."
- **First on-screen caption:** "YOU WAKE UP AND" (all-caps phrase blocks, white, with **one key word in red**, e.g. "SHARPER"; lower-middle).
- **First 2 seconds:** a fast blur-in to a red-faced Roblox kid in a propeller beanie lying in bed; at 1.5 s a close-up of his **fangs**; at 2 s he checks the mirror.
- **Rule visible by 2 s?** No "In this world" rule. It's a **second-person "you" horror** format; the hook visual (fangs) is at 1.5 s.
- **Premise:** "You" wake up with animal senses and urges; mom ties you up and nails the door; the ending reveals a real psychiatric condition (clinical lycanthropy). → **Creepy/horror** with a fact-reveal twist (Zack D. Films-style).
- **Beats:**
  - 0–8 s hook: sharp teeth, smelling the neighbour's dog across the street.
  - 8–15 s: "you're getting superpowers"; raw steak in the fridge.
  - 15–22 s: mom gives you a pill; "you throw it back up."
  - 22–30 s escalation: she ties your hands to the bed; you fall asleep staring at the family camping photo.
  - 30–38 s: you wake to mom "nailing your door shut"; the ropes are chewed through, "fibers stuck between your teeth".
  - 38–44 s: mom on the phone, "You guys have to come tonight", then muttering a prayer.
  - 44–51 s climax: you jump out the window and run at the dog on all fours; headlights; "your neighbor's car slams into you."
  - 51–59 s reveal: "This is clinical lycanthropy, where your brain is convinced you're turning into an animal. And now you can hear your mom scream, but you keep barking at the dog."
- **Twist:** It isn't a werewolf, it's a real delusion. Planted by "you don't see anything wrong when you check the mirror" (3 s). It reframes everything as mental illness.
- **Ending:** Scary/bleak (hit by a car, still barking). Ends on an image, not a question.
- **Tone:** Creepy/horror.
- **Lore signals:** none. The creator posts a "What animal would you be?" comment.
- **Audio:**
  - **Voice:** one narrator, second person, **~5.2 words/s (very fast)**. Pitch ≈ 180–210 Hz.
  - **Music:** a low sustained drone bed. **The bass drops out briefly at 3.0–4.5 s** (after the hook line), then a sustained low drone enters at ~6 s and holds. The texture gets noisier at 44–50 s (the chase/crash) before the reveal.
  - **SFX:** one big hit at 31.9 s (door being nailed).
  - Loudness median −18 dBFS.
- **Captions:** all-caps phrase blocks, white, red key word.
- **Look:** Roblox avatars with custom faces (red skin, fangs); dim bedroom/house interiors, then a night street with headlights. About 38 cuts in 59 s (~1.5 s).
- **Top 5 comments (~100 loaded):**
  1. @grEEn_guy-c00l (9.5K): "No this is actually called speed syndrome / . / (This is meant to be a joke / And also I didn't realize it was real I'm sorry I thought he was joking.)"
  2. @AbdElHamidBenali-i1x (4.5K): "My dumb ahh thought it was a vampire that ran out of controle"
  3. @johnnyboy1353 (2.9K, creator): "What animal would you be?"
  4. @OfficialOTG-1 (860): "It’s called “18 million Ishowspeed syndrome, where a person is overly exited over absolutely fucking nothing”"
  5. @Thisaccountisinactivelol (833): "Just for more explanation, this is specifically about wolves, it's called clinical LYCANTHROPY for a reason, it's extremely rare however."
  - **Latch onto:** meme jokes (IShowSpeed), misreading it as a vampire, explaining the real condition, the creator's "what would you be" prompt.

### Y8. IN THIS WORLD EVERYONE HAS A GIANT VERSION (HIT)
- **URL:** https://www.youtube.com/shorts/9K1bOjMUj7E · **Channel:** RealDanty (@Danty_Stories) · **Posted:** 2026-10-18 · **Views:** 13.9M · **Likes:** 271K · **Comments:** 945 · **Length:** 162 s · 720p
- **First spoken line (auto-transcript):** "In this world, everyone has a giant who is exactly like their true self."
- **First on-screen caption:** "in" / "world" (single words, white, black outline, ~66% down).
- **First 2 seconds:** frame 0 is black; at 0.5 s a **giant translucent grandma** looms behind a small grandma in a sunny village; at 2 s a giant dark figure behind a building.
- **Rule visible by 2 s?** Yes. Giant ghost-versions behind people at 0.5 s.
- **Premise:** At night everyone's "true self" giant wakes up; good giants build, evil ones destroy; Dante discovers the nicest kid at school leads the evil giants. → **Creepy/wonder (dark fantasy).**
- **Beats:**
  - 0–14 s rule: "When people fall asleep, the giants wake up… In the morning, nobody remembers anything".
  - 14–30 s world: "the streets… had been the scene of battles between giants just hours before."
  - 30–48 s inciting: Dante (the leopard-shirt, propeller-beanie character) wakes at 3:00 a.m. and sees the giants.
  - 48–62 s twist 1: the evil giant is "Noah from his class, the nicest kid in school, straight A's"; "Two more nights, then the tower falls and the world is ours."
  - 62–80 s: the tower holds the city together; the teacher laughs at his video ("Very good special effects"); Noah hands out candy.
  - 80–100 s confrontation: "I'm the real Noah. The one downstairs is just a mask."
  - 100–140 s plan and climax: he hides sleeping Noah in a warehouse rigged with a detonator: "You're nothing without him… He's the one who gives you life". The giant kneels: "Please, don't."
  - 140–162 s ending: the evil giants scatter; next day Noah: "Hey, want to sit with me today?" "I know who you really are. Don't talk to me."
- **Twist:** the nicest kid is the evil leader (planted by "nobody knows who the people around them really are", 10 s). The leverage twist is that the giant depends on its sleeping human.
- **Ending:** Tense/open; a cold last line. No loop.
- **Tone:** Creepy/dark fantasy. No warm beat.
- **Lore signals:** **the protagonist is "Dante" (leopard shirt and propeller beanie), the same character model that appeared in noirfilmsanimations' Instagram hit and robloxchiller's flop**, so this channel (RealDanty/"Danty") appears to be where that character originates. The creator pins an off-topic engagement-bait comment ("DROP HERE YOUR WILDEST RECIPES YOU KNOW…").
- **Audio:**
  - **Voice:** one narrator (third person) plus giant/teacher/Noah lines; one line is tagged ">>" in the transcript, which marks a speaker change. **~4.3 words/s (fast).** Pitch ≈ 180 Hz (lower than the other channels).
  - **Music:** loud, bass-heavy bed throughout (bass only ~5 dB under the voice), with a steadier pulse (~150 BPM detected); "[music]" tags throughout.
  - **Drop-outs:** none.
  - **SFX:** hits at 88.6 s and 91.8 s (crushing / the giant laughing so "the windows shook"), 143.7 s, 158 s and 161.6 s.
  - Loudness median −18 dBFS.
- **Captions:** single word, white with a black outline.
- **Look:** Roblox avatars with layered clothing and accessories; giants rendered as huge translucent/dark versions; village and church sets, many night scenes. About 107 cuts in 162 s (~1.5 s).
- **Top 5 comments (~100 loaded):**
  1. @alisinanucer (1.9K): "You’re telling me no one NO ONE else woke up at 3 am in the whole town"
  2. @Nightmarefuelfish (674): (a pasted cake recipe, replying to the creator's prompt)
  3. @Danty_Stories (646, creator): "DROP HERE YOUR WILDEST RECIPES YOU KNOW… ️"
  4. @TheFishjorleiam (510): "This story literally forgets that some people have to go to work at night shift."
  5. @aydenc-n2d (426): "that part was brutal holy ️ / wow 330 likes thanks guys"
  - **Latch onto:** plot holes about the rule, the creator's off-topic bait thread, the brutal climax.

### Y9. In This World, EVERYONE has a voice in their head (HIT)
- **URL:** https://www.youtube.com/shorts/Y7IyM87DmrQ · **Channel:** Ryex (@RyexRBLX) · **Posted:** 2026-10-25 · **Views:** 12.8M · **Likes:** 378K · **Comments:** 3,870 · **Length:** 145 s · 720p
- **First spoken line (auto-transcript):** "In this world, everyone is born with a robot voice in their head. We call her Sky."
- **First on-screen caption:** "WORLD" / "EVERYONE IS" (all-caps 1–3-word blocks, white, black outline, ~65% down). On-screen diegetic text like "Wake Up" appears in blue.
- **First 2 seconds:** a street of kids, each with a **glowing blue smiley-face orb** floating by their head; the red-haired narrator has a **red** orb (different). At 1–2 s a blond kid walks with his blue orb.
- **Rule visible by 2 s?** Yes. Blue "Sky" orbs by every head from frame 0, and the narrator's differs.
- **Premise:** Everyone hears the helper AI "Sky" except Leo ("empty head"); when Sky is hijacked to hunt him, she can finally talk to him. → **Creepy/sci-fi**, with a warm ending.
- **Beats:**
  - 0–15 s rule: Sky wakes you, "reminds you to look both ways", "whispers every answer on every test".
  - 15–35 s wound: "I'm the only person in the world who was born without Sky"; the doctor says "There's nothing in there"; called "empty head"; Tyler: "Hello, anyone in there?"; Dad: "You're not broken. You're special."
  - 35–48 s turn: mid-test the class glows blue and every kid says "Find Leo."
  - 48–62 s escalation: neighbours and police glowing, "Find Leo. Find Leo." Dad glows too: "Keep him here."
  - 62–75 s twist 1: "for the first time in my life, I heard a voice… Sky?" "Someone broke into my tower… They're using my voice to control everyone, everyone except you." His head "was always empty. It's the only place they can't get in."
  - 75–95 s chase: Sky guides him ("Left… Now right… Don't breathe"); Tyler almost spots him.
  - 95–112 s twist 2: in the tower the **doctor** is the villain: "I've been trying to get inside your head your whole life."
  - 112–130 s sacrifice: "Pull it, Leo… But if you do, I'll be gone forever." He pulls the switch.
  - 130–145 s ending: the doctor can't answer "what's 2 + 2?"; the town grabs him. "That night, I knocked on my own head. 'Hello? Anyone in there?' And this time, someone answered. 'Just me.' Sky whispered. **And if you can hear me, too, like and subscribe.**"
- **Twist:** The doctor who said "nothing in there" is the hijacker. Planted at 17–20 s. The "empty head" becomes the safe place. The last line flips Tyler's insult ("Hello, anyone in there?").
- **Ending:** Happy/warm. A callback loop to the insult line, plus an **in-voice CTA to like and subscribe**.
- **Tone:** Creepy (mind control) turning warm (Dad, Sky).
- **Lore signals:** the bully is again named "Tyler" and the hero "Leo" (common names across this genre). The comments run a meme ("Verity", "Falsity"…) and creator-name jokes.
- **Audio:**
  - **Voices:** the narrator plus a **separate female "Sky" voice**, Dad, the doctor and crowd chanting. The transcript marks speaker changes. **~4.9 words/s (very fast).** Measured pitch peaks at ~185 Hz and ~277–349 Hz (two or more voices, consistent with the kid narrator and the female Sky voice).
  - **Music:** very bass-heavy bed (bass ~2 dB under the voice), continuous. Brighter melodic layer for the first ~25 s (the world intro), then darker from ~28 s.
  - **Drop-outs:** none.
  - **SFX:** hits at 8 s, 44 s (the class glowing / "Find Leo") and 117 s (the switch).
  - Loudness median −17 dBFS.
- **Captions:** all-caps 1–3-word blocks, white with an outline.
- **Look:** Roblox avatars with detailed hair and flannel outfits; glowing blue orbs as the rule marker; suburb, classroom, bedroom, tower lab. About 92 cuts in 145 s (~1.6 s).
- **Top 5 comments (~100 loaded):**
  1. @wanbatoltv (1.9K): a long meme list of "verities" ("No. 1 Verity / No.2 Falsity / … / if you have ideas, drop your ideas in the reply section!"). One item contains a slur and is omitted here.
  2. @RyexRBLX (1.2K, creator): "Do you know what’s 2+2?  /  / BRO STOP SAYING VERITY OR FALSITY "
  3. @LucxasRL (938): "Kreekcraft be doing side quests"
  4. @JustCallMeMAM (596): "Gojo on side quests"
  5. @Ducki99-pt5 (409): "“Hey! It’s me! It’s Skyity!”"
  - **Latch onto:** a running meme from other videos (verities), streamer/anime jokes, quoting the punchline.

### Y10. In This World, MOVING is deadly (HIT)
- **URL:** https://www.youtube.com/shorts/HesZazDqE5M · **Channel:** Ryex · **Posted:** 2026-09-15 · **Views:** 11.1M · **Likes:** 171K · **Comments:** 1,670 · **Length:** 54 s · 720p
- **First spoken line (auto-transcript):** "In this world, moving is deadly. Once a day without warning, everyone has to go completely still."
- **First on-screen caption:** "WORLD" / "MOVING IS" (all-caps blocks, white; the key word "STILL" in red).
- **First 2 seconds:** a sunny front yard with three kids; a **tall yellow skeletal monster** looms behind them reaching in; at 1 s a red skull icon over a kid. Then a sunrise over the forest (1.5–2 s).
- **Rule visible by 2 s?** Yes. The monster plus a red skull "danger" icon by 1 s.
- **Premise:** Once a day everyone must freeze or monsters take you; Eric sacrifices himself for a friend who sneezed. → **Creepy/horror** with a twist ending.
- **Beats:**
  - 0–7 s rule.
  - 7–18 s setup: new kid Eric; the legend of "a kid two years ago who tripped mid-freeze… Everyone called him the one who failed."
  - 18–25 s inciting: walking home with Mason, a bell rings ("bow ring" in the auto-transcript); "Freeze now!"
  - 25–35 s escalation: monsters "checking each person one by one"; one creeps toward Mason, who sneezes.
  - 35–45 s climax: "He shoved Mason back and stepped [forward]… Don't take him, please"; the monster grabs both.
  - 45–54 s twist: he opens his eyes and a kid is "standing in front of him smiling. 'Welcome to Monster City.'"
- **Twist:** The taken aren't killed, they're brought to "Monster City" (implied: the kid "who failed" is there). Planted by the legend at 10–15 s.
- **Ending:** Open cliffhanger. **The creator pinned "Part 2? Comment if you want part 2 or not."**
- **Tone:** Creepy/horror; a brief loyal-friend beat.
- **Lore signals:** "Monster City" world-building, an explicit Part 2 ask, and the "Verity/Cruelty/Curiosity" meme from the same creator's comment sections (cross-video in-jokes).
- **Audio:**
  - **Voice:** a third-person narrator plus whispered/pleading lines, **~4.4 words/s (fast)**. Pitch peaks ~233 Hz plus others.
  - **Music:** very bass-heavy and loud (bass ≈ voice level; median −16.9 dBFS), continuous; no drop-outs detected.
  - **SFX:** cluster of hits early (5.1, 7.8, 14.4, 18.7 s), i.e. stings on the monster, the legend and the bell.
- **Captions:** all-caps 1–3-word blocks, red key word.
- **Look:** Roblox avatars (red-haired kid with big expressive anime-style faces in close-ups: crying, shocked), a yellow skeletal monster, suburb then night street. About 37 cuts in 54 s (~1.5 s).
- **Top 5 comments (~100 loaded):**
  1. @PjVitangcol (2.7K): "Verity and cruelty and last curiousty️ /  /  /  /  / Edit: omg  / Guys it's my first time getting alot of likes / Guys I'm crying right now omg"
  2. @RyexRBLX (1.5K, creator): "Part 2?  / Comment if you want part 2 or not.  / Edit: STOP SAYING VERITY "
  3. @Kyoko-i9x (938): "I like to think that the monsters are like delivery guys and humans are like pets in monster city so they get pets that other monsters order"
  4. @Wyatt-ee3tz (859): "Bro got taken to monster inc."
  5. @art_edt3z (758): "Verity, cruelty and curiousty doing side quest ️️"
  - **Latch onto:** the channel's running meme, **Part 2 requests**, theories about Monster City, Monsters Inc. jokes.

### Y11. In This World, Everyone Has 3 Steal Buttons (HIT)
- **URL:** https://www.youtube.com/shorts/e67RuR5nQR0 · **Channel:** ItsGuestCap · **Posted:** 2026-09-14 · **Views:** 9.8M · **Likes:** 147K · **Comments:** 521 · **Length:** 67 s · 720p
- **First spoken line (auto-transcript):** "In this world, everyone is born with three buttons on their wrist. Press one button and you can take anything from anybody."
- **First on-screen caption:** "In this WORLD" (italic phrase blocks, white, black outline, CAPS key words).
- **First 2 seconds:** a bright classroom; a kid's wrist shows **three glowing green buttons**; at 1.5–2 s a close-up of the wrist ("With three buttons on their WRIST").
- **Rule visible by 2 s?** Yes. Glowing wrist buttons at 0–2 s.
- **Premise:** Three steal-buttons; using them marks you as a thief. Rich bully Logan mocks Carter (2 buttons used) until he learns why. → **Emotional.**
- **Beats:**
  - 0–17 s rule plus social cost ("Use one and people think you're selfish… Use all three and everyone knows you as a thief").
  - 17–28 s: Logan, "the richest kid", is a target and avoids button-users, "especially Carter".
  - 28–37 s cruelty: "There's the thief. Who are you stealing next?" "Carter never defended himself. He'd just keep walking."
  - 37–45 s turn: a girl drops her money; "Carter gave every dollar back."
  - 45–62 s reveal: button 1 took money from "a rich, greedy kid because my little brother needed an operation"; button 2 took "someone's new car because my mom had been walking to work every day"; "I knew everyone would hate me for it, but I'd do it again."
  - 62–67 s ending: "he stopped seeing a thief. He saw someone who was willing to be hated to give the people he loved happiness."
- **Twist:** The "thief" is a Robin Hood. It's the same structure as this channel's Y1 (the kid judged by a visible number is secretly selfless). Planted by "never defended himself".
- **Ending:** Bittersweet/moral; a final reframe line.
- **Tone:** Emotional.
- **Lore signals:** the same template and moral as other ItsGuestCap Shorts. **The creator pins a moral "would you" question:** "Would you use your button to help a friend or someone you love... even if it meant people would think you're a thief?"
- **Audio:**
  - **Voice:** one narrator plus character lines (transcript ">>" marks), **~4.8 words/s (very fast)**. Pitch ≈ 220–240 Hz (an 87 Hz peak is music bass). Same voice profile as Y1 and Y5 (same channel).
  - **Music:** a light, low-bass bed (bass ~25 dB under the voice). **Two clear drop-outs at 34.1–35.1 s and 36.1–37.6 s**, silence around "But still, Carter never defended himself. He'd just keep walking." (dramatic pauses).
  - **SFX:** none detected.
  - Loudness median −17.8 dBFS.
- **Captions:** italic phrase blocks, white, black outline, CAPS key words.
- **Look:** blocky Roblox avatars, bright classroom, hallway, hospital. About 50 cuts in 67 s (~1.3 s).
- **Top 5 comments (~100 loaded):**
  1. @LiuRyan-jx8jo (1.7K): "“Steal everyone’s buttons”"
  2. @andriyliut6984 (647): "Carter looks like hxsain"
  3. @ReyTek764 (244): "idea. take 2 slots for new buttons with one button / and steal from bad rich ppl so that they can't do evil stuff"
  4. @Itsguestreal (179, creator): "Would you use your button to help a friend or someone you love... even if it meant people would think you're a thief? "
  5. @MoeezAli-x7tudur (76): "I would use it in specific conditions"
  - **Latch onto:** loophole hacks, a lookalike joke, answering the creator's moral question.

### Y12. In This World, Your Son Is Haunted (HIT)
- **URL:** https://www.youtube.com/shorts/j1vrfEnEiI8 · **Channel:** Gelo Stories · **Posted:** 2026-10-12 · **Views:** 9.6M · **Likes:** 335K · **Comments:** 694 · **Length:** 120 s · 720p
- **First spoken line (auto-transcript):** "In this world, if you kill someone, they're reborn as your kid."
- **First on-screen caption:** "In this world" (short phrases, white, with the key word **in red**, e.g. "kill").
- **First 2 seconds:** on a cliff edge, an orange-haired man falls/is pushed while another watches; at 2 s a father holds a newborn in a nursery.
- **Rule visible by 2 s?** Yes, shown as an action (a death, then a baby) by 2 s. There's no persistent marker.
- **Premise:** Killed people are reborn as their killer's child ("haunted kids"); a dad who accidentally drowned his best friend suspects his son is him. → **Creepy setup, emotional payoff.**
- **Beats:**
  - 0–10 s rule plus 2 gags: "The bus driver's son flattens his tires every night. The doctor's daughter breaks her glasses every morning."
  - 10–14 s the hospital question: "Do you owe anyone anything?"
  - 14–25 s backstory: best friend Fade, "a green cap… we fished every Sunday"; the boat turned too fast; "Only his cap came back up."
  - 25–40 s guilt: hides the rods; a flower at his grave every Sunday; at the hospital "I said no. I lied."; the baby "didn't cry, just watched me, like he knew me."
  - 40–60 s escalation (x4 clues): at seven Tommy swaps a red cap for a green one; stands in the doorway watching him sleep; the hidden rods appear clean on his bed; a calendar with the accident day circled in red.
  - 60–80 s climax: "Dad, let's go fishing at the lake"; the sky turns black; he falls in; "This is it. He waited seven years…"
  - 80–110 s twist: "a tiny hand grabbed my arm. Tommy had jumped"; "I forgave you years ago. I saw every flower… You cried in your sleep and said my name… I'm not back for revenge. We never finished fishing."
  - 110–120 s ending: "We fished until the moon rose. **Like and subscribe or I'm your next kid.**"
- **Twist:** The haunted son came back out of love, not revenge. Planted by the flowers at the grave (26 s) and "watching me sleep" (44 s). The creepy clues are reinterpreted.
- **Ending:** Warm/emotional, with a joking in-voice CTA.
- **Tone:** Creepy first half, strongly emotional ending.
- **Lore signals:** the same premise was posted on Instagram by @cipher_shorts ("In This World, Your Son Is Haunted!!!", 2.8M plays, Oct 15). A top commenter suspects the story was copied between animators.
- **Audio:**
  - **Voices:** narrator (dad, first person) plus a nurse and the child; the transcript uses ">>" speaker changes ~15 times, i.e. **multiple voices**. **~3.9 words/s (fast, slower than the others).** Pitch ≈ 200 Hz, with peaks at 208 Hz and 247 Hz (dad vs child).
  - **Music:** continuous bed with low bass (−15 dB under the voice). A quiet tonal moment ~15 s (the boat memory).
  - **SFX:** **14 hits, clustered 72–111 s** (storm, wave, splash, rescue). The most SFX-heavy Short in the set.
  - Loudness median −17.6 dBFS.
- **Captions:** short phrases, white with red key words, lower third.
- **Look:** Roblox avatars (stylised hair, a green cap as the recurring prop), cliff, nursery, bedroom, lake, a storm. About 84 cuts in 120 s (~1.4 s).
- **Top 5 comments (~100 loaded):**
  1. @Et3rnal_Sugar_Cooki3 (4.6K): "IMAGINE IF YOU ACCIDENTALLY KILL YOUR PARTNER AND THEY COME BACK AS YOUR CHILD?"
  2. @adamakbarali2358 (1.3K): "This is enough to make a grown man cry"
  3. @Jane56789 (997): "If you had kids of 4 and then kill somebody you can’t have kids because you already have kids"
  4. @V1vidian (894): "I swear I heard the exact same story days before, made by a different animator I forgot the name of. The story might've been stolen? I'm not really sure. / Edit: Orrr it could've been a story shared online (before the animation I saw) that was soon animated"
  5. @Supernova_goji (368): "To be honest , if this existed me and my friend would intentionally kill one another...FOR FUN / Edit: thanks"
  - **Latch onto:** "what if" rule scenarios, emotional reactions, plot logic, originality.

### L1. In This World, Everyone Can Replay Any Memory They Want (LOW for this channel)
- **URL:** https://www.youtube.com/shorts/fp-F6vhgwOc · **Channel:** ItsGuestCap (same as Y1, Y5, Y11) · **Posted:** 2026-10-18 · **Views:** 106K · **Likes:** ~2K · **Comments:** 26 · **Length:** 55 s
- **First spoken line (auto-transcript):** "In this world, everyone has a device that replays any memory you want."
- **First on-screen caption:** "In this WORLD" (the channel's usual phrase-block style; the key word "MEMORY" in **cyan**).
- **First 2 seconds:** a close-up of a glasses girl holding a small glowing **device** at her chest; at 1.5 s a boy in a school hallway holding one.
- **Rule visible by 2 s?** Partly. A small handheld device, not a marker over heads; the memories themselves aren't shown until ~4 s.
- **Premise:** Everyone replays their best memory to show off; Caleb replays a "boring" 5 seconds of a kitchen. → **Emotional.**
- **Beats:**
  - 0–12 s examples (dog, championship, teacher's wedding).
  - 12–22 s: Marco has hundreds of great memories; "A boring memory meant a boring person."
  - 22–33 s: Caleb replays "the same 5 seconds… a kitchen and a woman putting a plate down"; Marco calls him "the most boring person alive."
  - 33–45 s: Marco asks why.
  - 45–55 s reveal: "That's my mom and my little brother. That was the first night we ever had enough food for all three of us… this one is still the best day of my life." Marco "never saw a kid happy to watch his family finally [eat]…"
- **Twist:** The "boring" memory is about poverty and family. The same reversal as Y1/Y11, but **with no danger, no ticking number, no escalation and no confrontation**; one reveal, delivered by dialogue.
- **Ending:** Bittersweet moral. It cuts off mid-sentence.
- **Tone:** Emotional, low-stakes.
- **Audio:**
  - **Voice:** the same narrator profile as the channel's hits, ~5.0 words/s (very fast); pitch ≈ 216–230 Hz.
  - **Music:** a very light bed (bass ~26 dB under the voice, the lowest in the set), short drops at 17.5 s and 32.5 s.
  - **SFX:** hits at 38.8 s and 42.6 s.
  - A commenter noticed: "For the first time the 'In this world' is quieter".
- **Captions/look:** the same template as the hits (phrase blocks, CAPS key words, white flashes, school sets). About 34 cuts in 55 s.
- **Comments (19 loaded):**
  1. @Itsguestreal (17, creator): "what’s a memory you’d replay forever ?"
  2. @ArzadistanBall (9): "For the first time the “In this world” is quieter"
  3. @FionaKoubaroulis (9): "I would replay when my parents were still together………"
  4. @almacatu-l2n (6): (a long fan-written story idea)
  5. (no further comments with likes)
- **Why lower than the channel's hits (observed differences):** the rule has no cost or danger (you can't lose anything); the marker isn't visible over people; there's no ticking/visible escalation; the conflict is one insult; the music is the quietest of the set.

### L2. In This World, TOUCH is deadly (LOW for this channel)
- **URL:** https://www.youtube.com/shorts/9lp9G-glh6k · **Channel:** Ryex (same as Y9, Y10) · **Posted:** 2026-09-14 · **Views:** 299K · **Likes:** 5.8K · **Comments:** 210 · **Length:** 48 s
- **First spoken line (auto-transcript):** "In this world, touch is deadly. One accidental touch and you're gone."
- **First on-screen caption:** "WORLD TOUCH" / "IS DEADLY" (the channel's all-caps blocks, key word in red).
- **First 2 seconds:** the **same opening shot/kids as Y10 "MOVING is deadly"** (a red-haired kid in front of a house, a red skull icon) with a glitchy red effect; then a boarded-up abandoned house.
- **Rule visible by 2 s?** Only as a generic red-skull icon. Touch itself can't be shown as a marker.
- **Premise:** Touching anyone kills them; "toucher" Nathan, bullied by Theo, has to grab Theo when he slips off a cliff. → **Creepy/peril with a moral.**
- **Beats:**
  - 0–8 s rule ("Nobody's touched another person in 300 years… Hugs are just a word in old textbooks now").
  - 8–20 s: Nathan "always had trouble keeping his hands to himself"; Theo calls him "the toucher"; Nathan wears gloves.
  - 20–33 s: a mountain trip; Theo slips and hangs on a ledge, his rope loose.
  - 33–48 s climax: "He got down on his stomach, reached over the edge, and grabbed Theo's wrist with his bare hand. He pulled him back up. Theo looked at Nathan. 'How?'" It ends there; the answer is left to the comments (only *accidental* touch kills).
- **Twist:** the loophole is in the wording ("One **accidental** touch"). Planted at 2 s. The ending is ambiguous; the creator turns it into a quiz in the comments.
- **Ending:** Ends on an unanswered question ("How?"), i.e. a riddle. The creator pins "Why can nathan touch? Correct answer gets a heart!"
- **Tone:** Creepy/peril into a moral.
- **Audio:**
  - **Voice:** the same channel narrator, ~4.4 words/s; measured pitch is higher here (≈285 Hz median) with a wide spread.
  - **Music:** continuous, light bass (−19 dB under the voice); no drop-outs.
  - **SFX:** one hit at 2.7 s.
- **Captions/look:** the same as Y9/Y10; **reused opening footage** from Y10; about 30 cuts in 48 s.
- **Top comments (~100 loaded):**
  1. @dutdutful (334): "Explanation: / The narrator said "Any ACCIDENTAL Touch and your gone" But nathan didn't touch him by accident /  / Edit: GUYSSS I WAS RIGHT!! (I got hearted but due to the edited message it disappeared)"
  2. @RyexRBLX (108, creator): "Why can nathan touch?  / Correct answer gets a heart! "
  3. @Poweraaam (52): "the TOUCHER is a wild nickname"
  4. @lemonVR_the_the3rd (45): ""The toucher" ayo pause"
  5. @redmuhammadgamer-Roblox (10): "I know if someone help the stranger and he not die"
- **Why lower than the channel's hits (observed differences):** a reused opening (the same intro shot as "MOVING is deadly", which the channel posted the next day and which got 11M); the rule is invisible; the twist is unclear enough that it needs a comment quiz; it's short with one beat of escalation; no emotional/family stake; the "toucher" nickname drew innuendo jokes.

### L3. IN THIS WORLD YOU HAVE TO WIND UP CREATURE❤️ (LOW for this channel; the same video as Instagram flop #16)
- **URL:** https://www.youtube.com/shorts/asxZdJwcJb4 · **Channel:** RealDanty (same as Y8) · **Posted:** 2026-10-24 · **Views:** 177K · **Likes:** hidden · **Comments:** 64 · **Length:** 121 s
- **Key finding:** this is **the exact video** that @robloxchiller posted on Instagram on Oct 25 (4.6K plays, our flop #16): same title, same frames, same narration. robloxchiller is re-uploading RealDanty's YouTube Shorts, which also explains the "Dante" character showing up across accounts. **The story underperformed on both platforms** (177K vs RealDanty's 9–14M hits). That points at the video itself, not the Instagram account.
- **First spoken line (auto-transcript):** "In this world, people have to go underground every 8 hours to wind up a giant monster sleeping beneath the city." (This matches the Instagram captions exactly.)
- **First 2 seconds:** the same as the IG notes: a rooftop shot, a school-bus street with cameo characters, then near-black underground silhouettes by 1 s.
- **Beats / twist / ending:** as in Instagram flop #16 (the monster whispers "Help", the protector monster, the jealous mayor, "Thank you for finally listening").
- **Audio:**
  - **Voice:** a third-person narrator plus Dad, mayor and monster lines; **~4.3 words/s** (521 words / 121 s); pitch ≈ 190–205 Hz.
  - **Music:** bass-heavy bed (−4 dB under the voice); a sustained low drone from ~26 s ("Never listen to it" / the elevator going down) to the end; no drop-outs.
  - **SFX:** hits at 11.2 s, 68.5 s (the eye opens), 86.6–87.5 s (the mansion crushed), 107.7 s.
  - The audio treatment is the same as the channel's 13.9M hit (Y8), so **audio doesn't explain the gap**.
- **Comments (53 loaded):**
  1. @Mardox_SCP (19): "Reading classified SCP files can lead to your termination"
  2. @primarytrend7915 (19): "Conquest at the start"
  3. @Manuel-h2t9o (17): "New style is peak"
  4. @CHAOS_COMMANDER-OFFICIAL (15): "Bros what was Herobrine doing "
  5. @Johntyznik (11): "WHY WAS @REALLYRAFF IN THIS VIDEO"
  - **Latch onto:** spotting cameo characters in the opening crowd (Conquest, Herobrine, a YouTuber), not the story.
- **Why lower than the channel's hits:** the same issues as on Instagram: a confusing, dark first 2 s full of unrelated cameos (comments are about the cameos); the rule involves 12 workers, not everyone, so there's no "what would I do"; third-person Dante with no personal stake; a political-vault ending rather than a loved one; the title is grammatically broken ("YOU HAVE TO WIND UP CREATURE❤️").


## Part B: audio of 5 Instagram hits (re-watched with sound analysis)

Same method as above, on the Instagram reels from round 1. Spoken words were already captured in round 1, so this section covers audio only.

| Reel | Account | Length | Voice pitch (voice-dominant median) | Pitch spread | Voices | Music bed | Bass vs voice | Drop-outs | Big music change | SFX hits | Loudness |
|---|---|---|---|---|---|---|---|---|---|---|---|
| [Deo_lQhs48L](https://www.instagram.com/reel/Deo_lQhs48L/) 1,000,000 Steps | craftee_films | 112 s | ~231 Hz | 5.8 st | narrator; pitch clusters 185/233/277 Hz (narrator plus voiced lines) | continuous, start to end | −15 dB | none | busier, bass-heavier texture from **54 s** (stroller starts rolling) through the rescue | 1 (54.1 s, stroller) | −18 dBFS |
| [DfEbVWLhKIl](https://www.instagram.com/reel/DfEbVWLhKIl/) Never Turn Around | craftee_films | 142 s | ~210 Hz | 6.8 st | narrator plus Dad/Mom lines (clusters 147–370 Hz) | continuous; lighter first half | −20 dB | none | **sustained low drone swells in at ~88–90 s** (night walk to Dead Man's Drop) and holds to the end | 7 (22–28 s gags, 40–42 s quarry, 68.6 s "spider on your back") | −19 dBFS |
| [DevhviPRj0Y](https://www.instagram.com/reel/DevhviPRj0Y/) Magic Line | robloxstoriesdaily | 66 s | ~223 Hz | 7.0 st | narrator plus Dad line | dense, continuous | −10 dB | none | **sub-bass drone rises at ~25 s** (the storm hits) and stays | 3 (15.8, 38.4, 46.9 s) | −19 dBFS |
| [DfE4rdHRx6U](https://www.instagram.com/reel/DfE4rdHRx6U/) Kevin | noirfilmsanimations | 143 s | ~212 Hz | 6.7 st | narrator plus Blaze/Tornado lines | continuous, light for the comedy section | −23 dB | none (brief thinning 84–86 s) | **heavy low drone enters ~88 s** (shelter, Grandma's book) and holds through the tornado walk | 4 (3.2 s Sky flies; 84 s; 100–101 s into the tornado) | −19 dBFS |
| [DezgcRbz0ao](https://www.instagram.com/reel/DezgcRbz0ao/) Balloon | green_brorants | 106 s | ~217 Hz | 6.8 st | narrator plus Mom/Doran/Sam lines | light, continuous, almost no bass | −34 dB | none | low "boom" hits at ~5 s (pop), ~67 s (lights flick on) and ~93 s (Doran's balloon bursts) | 3 (43.6, 74.9, 79.0 s) | −18 dBFS |

**Instagram audio takeaways:**
- **One young-sounding narrator** in all five: ~210–231 Hz median, moderately expressive (6–7 semitones spread), with other characters' lines in the same reel.
- **A music bed never stops.** No drop-outs anywhere in these five, unlike several YouTube hits.
- **The main music move is a sustained low drone/bass that enters at the turn and stays to the end:** at 25 s (Magic Line), 54 s (Steps), ~88 s (Never Turn Around, Kevin).
- SFX are sparse (1–7 per reel) and land on story beats (a pop, the storm, the reveal), not on every cut.
- Mixes are loud and compressed (median −18/−19 dBFS), the same as YouTube.



## Part C: top 2 reels from capybluh, cipher_shorts and dylanstoriesyt

Ranked by plays within Aug 1 – Nov 1 (from round 1's scan). The cipher_shorts #2 slot is a tie at 2.8M; see C4.


### C1. Mom holding an umbrella over me (capybluh, #1 by plays)
- **URL:** https://www.instagram.com/reel/DcGvClbEiWG/ · **Account:** @capybluh · **Posted:** 2026-08-16 · **Plays:** 10.2M · **Likes:** 1M · **Comments:** 10K · **Length:** 58 s · 1080p
- **First spoken line:** none. **No narration** (voice detected in <10% of frames; it's music only).
- **First on-screen caption:** a fixed meme header at the top for the whole video: "When I feel Mom's love". Post caption: "Mom holding an umbrella over me".
- **First 2 seconds:** a rainy school front ("SCHOOL" sign). Kids are picked up under blue and red umbrellas held by their moms; the classic yellow-and-blue **Noob** stands alone in the rain. At 2 s a close-up of the Noob's sad face.
- **Rule visible by 2 s?** No rule. It's a **wordless, meme-captioned emotional montage**; the situation (rain, umbrellas, a lonely kid) is clear by 1 s.
- **Premise:** Over the years Mom always holds the umbrella over him; she ages and dies; he ends up holding the umbrella over her grave. → **Emotional.**
- **Beats (visual):**
  - 0–8 s: the Noob alone in the rain at school.
  - 8–20 s: Mom (purple shirt, red hair) arrives and holds the umbrella over him.
  - 20–37 s time passes: the son grows, Mom's hair turns **grey**, she still holds the umbrella.
  - 41–45 s: a gravestone reading "MOM" with her photo.
  - 45–55 s: the grown Noob alone in the rain at the cemetery.
  - 55–58 s: **he holds the umbrella over her grave** (the role reversal).
- **Twist:** the role reversal at the end, set up by the opening umbrella image.
- **Ending:** Bittersweet; a visual loop of the umbrella motif.
- **Tone:** Emotional (grief).
- **Lore signals:** the classic Noob avatar as an everyman; no series.
- **Audio:**
  - **Voice:** none.
  - **Music:** a **song with a strong regular beat** (the strongest pulse measured in the whole study, ≈100 BPM detected), continuous. It gets fuller/heavier from ~25 s (the aging montage). No drop-outs.
  - **SFX:** hits at 1.2 s, 10.2 s and 16.5–17.3 s (umbrella/rain moments) and 57.3 s (the final umbrella).
  - Loudness median −17.6 dBFS.
- **Captions:** a single fixed top header (white text on the frame); a "capybluh" watermark.
- **Look:** classic Roblox avatars (Noob, the mom gets grey hair); rainy school, street, cemetery; grey overcast lighting with rain VFX. About 24 cuts in 58 s (one every ~2.4 s, slower than the narrated hits).
- **Top 5 comments (~65 loaded):**
  1. @mr.patistouta (70,489): "I swear I just cry 😭"
  2. @flixhitzz (56,180): "Men see .. Men Stop .. Men Cry 😭😭"
  3. @yuthiel_leon (29,356): "Ni puedo que un video de roblox casi me ase llorar"
  4. @ilove_your_mommy (25,336): "i miss my mama even tho she is across the room 😭💔🥀"
  5. @tauane_santooo (20,961): "Eu chorando com a histórinha de Roblox 💔🥀"
  - **Latch onto:** **admitting they cried**, missing their mom, multilingual reactions (no words in the video means a global audience).

### C2. The burden of being a provider (capybluh, #2 by plays)
- **URL:** https://www.instagram.com/reel/DdXClCGEoS4/ · **Account:** @capybluh · **Posted:** 2026-09-16 · **Plays:** 9.0M · **Likes:** 836K · **Comments:** 4,818 · **Length:** 51 s
- **First spoken line:** none. No narration; music only.
- **First on-screen caption:** fixed top header "When I feel Dad's love" (the same meme template as C1). Post caption: "The burden of being a provider".
- **First 2 seconds:** a Noob kid at home turns, smiling, holding up a **"HOT & delicious PIZZA" flyer** (a full-frame close-up at 2 s).
- **Rule visible by 2 s?** No rule; the want (pizza) is clear by 1–2 s.
- **Premise:** The kid asks for pizza; the mustached dad checks his near-empty wallet, works late, buys the pizza, and later quietly eats the leftover crusts. → **Emotional.**
- **Beats (visual):**
  - 0–5 s: the pizza flyer request.
  - 5–6 s: Dad opens his **wallet** (a few bills).
  - 7–13 s: office, the boss, Dad working late at a computer in the dark.
  - 16–20 s: the pizza shop.
  - 22–28 s: Dad brings the box home.
  - 32–40 s: the kid eats happily.
  - 42–51 s: Dad alone at the counter eating the **leftover crust** from the box.
- **Twist:** a quiet reveal that Dad goes without (the crust), set up by the wallet shot at 5 s.
- **Ending:** Bittersweet; ends on a held shot.
- **Tone:** Emotional.
- **Audio:**
  - **Voice:** none.
  - **Music:** a song with a strong regular beat (≈100 BPM, a strong pulse, very similar to C1, probably the same or a similar sad-pop track). Continuous, no drop-outs.
  - **SFX:** hits at 0.6 s, 10–11 s (office), 30 s (the pizza arrives).
- **Captions:** a fixed top header only; a "capybluh" watermark.
- **Look:** classic Noob avatars (Dad has a mustache); home, office, pizza shop; flat bright lighting with a dark office night scene. About 31 cuts in 51 s (~1.6 s).
- **Top 5 comments (~69 loaded):**
  1. @ym_sebas (130,525): "Bro, this hits hard."
  2. @sophijpn__31 (51,010): "Why do I feel like dads are underrated now😢"
  3. @yxngnarrow (47,472): "ok now im crying"
  4. @imrane_legend15 (26,594): "Thats enough to make a grown man cry"
  5. @aam.shs (25,783): "19 yo male crying to Roblox reels 😭✌🏻"
  - **Latch onto:** crying confessions (especially young men), appreciation for dads.

### C3. I Broke My Boss's Windshield 😳 (cipher_shorts, #1 by plays)
- **URL:** https://www.instagram.com/reel/DecPA_UpWqr/ · **Account:** @cipher_shorts · **Posted:** 2026-10-13 · **Plays:** 4.4M · **Likes:** 288K · **Comments:** 192 · **Length:** 111 s · 720p (looks re-uploaded: soft image)
- **First spoken line (from burned-in captions):** "[I] smashed a golf ball through my boss's windshield." (The first caption tile at 0.1 s reads "smashed"; the opening "I" wasn't captured.)
- **First on-screen caption:** "smashed" (single **yellow** words with a dark outline, lower-middle).
- **First 2 seconds:** a sunny golf course; an adult Roblox golfer swings; at 1.5–2 s the ball smashes a parked blue car's windshield (a crack effect).
- **Rule visible by 2 s?** No rule. A **plain comedy story** ("I…" first person, an adult narrator).
- **Premise:** A terrible golfer's wild shots keep accidentally taking out criminals; he thinks he's being rewarded for recycling. → **Comedy.**
- **Beats (escalation by repetition):**
  - 0–14 s: the windshield shot; the chief pins a medal on him ("the city owes you one"); he assumes "it's the recycling. I rinse everything."
  - 16–27 s: a slice over the highway; Monday two detectives kick down his door and salute: "Thank you for Saturday."
  - 27–41 s: "So I recycled harder… rinsed the cans twice"; a ball disappears into a cloud ("That night the navy sent…"); another into the lake (submarine 781).
  - 41–50 s: the golf course gives him his own parking spot; the club flies over the clubhouse.
  - 50–66 s: a van follows him ("just keep missing, sir"); a man in a suit from a bush: "do not take a lesson"; "a senate hearing about your backswing."
  - 66–80 s: a general: "aim at the hole"; "the ball went the other way… stared through his binoculars."
  - 80–100 s twist: the president shows him a room of bagged golf balls labelled as exhibits ("ART THIEF", an escaped prisoner "in a cornfield", "SPY DRONE").
  - 100–111 s punchline: "son, you've never missed. You just never hit what you were aiming at… So it's not the recycling." "honestly, you've been putting glass in…"
- **Twist:** every miss was a hit on a criminal; the running recycling gag pays off at the end.
- **Ending:** Comedic punchline; loops back to the recycling gag.
- **Tone:** Comedy. Not creepy, not emotional.
- **Audio:**
  - **Voice:** a single adult narrator (first person) plus side characters, **~4.5 words/s**. **Measured pitch ≈ 177 Hz with low variability (5 semitones SD), the most monotone voice in the set** (a deadpan read). The narration might be AI, but that's an inference.
  - **Music:** **barely any music.** The quietest background of all 30 videos (the noise floor between words ≈ −34 dBFS). **Several silent beats** at 5.4, 9.0, 26.2, 53.7, 56.7 and 59.9 s, i.e. **pauses for comedic timing.**
  - **SFX:** none above threshold.
- **Captions:** single yellow words with an outline, plus diegetic signs/labels (hole numbers, "EXHIBIT" tags).
- **Look:** adult Roblox avatars, golf course, house, navy, a president's office; bright daylight; letterboxed. About 48 cuts in 111 s (~2.3 s).
- **Top 5 comments (~57 loaded):**
  1. @la.vod (24,969): "The recycling ending got me"
  2. @sushi.53_ (10,735): "this really happened btw i was the club"
  3. @johnny.hockeyy7 (3,907): "This really happened I was the thief"
  4. @hanniiii404 (2,527): "They were NOT hugging"
  5. @nyxyshark (1,437): ""you didn't miss, you just never hit what you were aiming at" goes kinda hard"
  - **Latch onto:** the callback punchline, "this really happened" bits, quoting the best line.

### C4. In This World, Your Son Is Haunted!!!😭 (cipher_shorts, joint #2 by plays)
- **URL:** https://www.instagram.com/reel/DeiGM6xymdf/ · **Account:** @cipher_shorts · **Posted:** 2026-10-15 · **Plays:** 2.8M · **Likes:** 335K · **Comments:** 463 · **Length:** 120 s · 720p
- **Selection note:** cipher_shorts' #2 spot is a tie at 2.8M (the grid rounds) between this reel and "Everyone Can Freeze Time For 10 SECONDS". I picked this one because it allows a direct cross-platform comparison.
- **Key finding:** **this is the identical video to YouTube hit Y12** (Gelo Stories, posted Oct 12, 9.6M views): same frames, same 119.6 s length, matching audio measurements (pitch ≈ 200 Hz, bass −15 dB, the same SFX cluster at 72–111 s). cipher_shorts re-posted it 3 days after the YouTube upload. **So all fields (first line, beats, twist, ending, tone, look, audio) are as in Y12.**
- **First spoken line / caption:** "In this world, if you kill someone, they're reborn as your kid." Captions: "In this world" → "if you **kill**" (red key word).
- **Audio (measured on the Instagram copy):** pitch ≈ 193–200 Hz; bass −15 dB under the voice; continuous bed; 9 SFX hits clustered at 72–111 s (storm/wave/rescue); the same as YouTube.
- **Top 5 comments (~74 loaded):**
  1. @smyth._2 (49,123): "So my bsf is my son.WIN WIN"
  2. @straw_hat_911 (23,234): "Two types of people 😂"
  3. @vhinzandreibacsan (13,610): "What if you never killed someone?"
  4. @icefairykirno (6,041): "now that's a real homie"
  5. @dolled_upz (3,381): (sticker/GIF, no text)
  - **Latch onto:** joke "what-ifs" about the rule (best friend as son), the friendship payoff. Lighter and more jokey than the YouTube comment section on the same video.

### C5. The School Lockdown 😳 (dylanstoriesyt, #1 by plays)
- **URL:** https://www.instagram.com/reel/Db_lMwqAlZD/ · **Account:** @dylanstoriesyt · **Posted:** 2026-08-13 · **Plays:** 3.2M · **Likes:** 167K · **Comments:** 392 · **Length:** 60 s
- **First spoken line (from captions):** "I was in class when they announced a lockdown because there was a killer clown in the school."
- **First on-screen caption:** "i was" (lowercase white 1–3-word chunks with a dark outline, ~72% down).
- **First 2 seconds:** a classroom; a wide-eyed, terrified student close-up at 0.5 s; at 2 s **a clown holding a knife** stands in a dim hallway.
- **Rule visible by 2 s?** No rule. A **plain first-person horror story**; the threat (a knife clown) is on screen at 2 s.
- **Premise:** During a lockdown, a classmate (Marcus) leads six kids into a closet; only five come out; the clown turns out to be Marcus. → **Creepy/horror.**
- **Beats:**
  - 0–4.5 s hook: the lockdown, "a killer clown in the school".
  - 4.5–14 s: lights off; Marcus pulls me to the supply closet; "Six of us crammed inside."
  - 14–22 s tension: "Footsteps stopped right outside… Someone knocked twice, slow and hard. Nobody moved."
  - 22–33 s release: sirens, police, "safe to come out", they file out.
  - 33–41 s turn: "Six kids had gone into that closet, only five came out… Marcus was gone."
  - 41–50 s: a full sweep, "No sign of him anywhere."
  - 50–60 s twist: they catch the clown at a side exit; "They pulled off his mask… It was Marcus. He had never actually gone into the closet with the rest of us. He could have killed all of us but he didn't. Why?"
- **Twist:** the helper is the killer. Planted at 7–11 s ("grabbed my arm… safest spot"). It contradicts the head count, which is a deliberate plot hole that commenters debate.
- **Ending:** Scary, **ending on an open question ("Why?")**, which drives theory comments.
- **Tone:** Creepy/horror. No warmth.
- **Audio:**
  - **Voice:** one first-person narrator, **~4.0 words/s**. **Pitch ≈ 215–220 Hz with very low variation (4 semitones SD), a single, steady, very even read.** That evenness is consistent with TTS, but it's an inference.
  - **Music:** a quiet, low, continuous drone bed (bass −10 dB under the voice); no drop-outs; no beat.
  - **SFX:** none detected (the knocks are narrated, not heard as hits above threshold).
- **Captions:** lowercase 1–3-word chunks, white with an outline.
- **Look:** Roblox avatars with expressive custom faces (wide eyes); a dim classroom, hallway and closet; a clown avatar with a knife; police lights. About 24 cuts in 60 s (~2.5 s, slower).
- **Top 5 comments (~82 loaded):**
  1. [username redacted] (23,592): "He probably liked u ig (in a friendly way)"
  2. @_ryderharrison_ (15,652): "Wait, if he was in the closet, who knocked on the door?"
  3. @douglasmcintoshiii (7,280): "Wait he got locked in the class with them how'd he get out without anyone noticing?"
  4. @youssef88305 (2,429): "Marcus is actually smart since he was locked inside the classroom he knocked on the door inside the classroom opened the door making everyone think the killer was outside then he continued on his day"
  5. @jms.bxrti (856): "Marcus has a split personalities and marcus is just trying to protect them, and look at marcus when he got caught, he was confused why were they detaining him"
  - **Latch onto:** **answering the "Why?"** and debating plot holes (theories).

### C6. You Can’t Stand In The Same Spot 😭 (dylanstoriesyt, #2 by plays)
- **URL:** https://www.instagram.com/reel/De0A_WjBahz/ · **Account:** @dylanstoriesyt · **Posted:** 2026-10-22 · **Plays:** 2.9M · **Likes:** 152K · **Comments:** 263 · **Length:** 137 s
- **First spoken line (from captions):** "In this world nobody can stay in one place for more than an hour."
- **First on-screen caption:** "in" (lowercase white 1–3-word chunks, ~72% down).
- **First 2 seconds:** a suburban street with a man in a captain's uniform; at 1 s a kid reads under a big **street clock**; at 2 s a close-up of the clock face.
- **Rule visible by 2 s?** Partly. A **clock** as the timer motif by 1–2 s; the sinking is shown at ~4–7 s.
- **Premise:** Stand still for 60 minutes and the ground swallows you, then spits you out in your yard an hour later; kids vanish on the "free night boat" because water never lets them go home. → **Creepy rule** with a clever-hero payoff.
- **Beats:**
  - 0–10 s rule ("the ground under you turns soft like mud and you sink… then an hour later the ground spits you back out in your own front yard covered in dirt").
  - 10–25 s gags: movies are 59 minutes; desk switches every half hour; "I've woken up in our front yard covered in worms twice in one night."
  - 24–33 s: rich families sleep on the night boat; Mr. Mooney lets one kid sleep free each night.
  - 33–42 s inciting: best friend Max is picked ("ran down the dock like it was Christmas") and doesn't come home.
  - 43–52 s mystery: missing posters going back 30 years ("Danny, missing since 1994"), all after the free boat; "you can't sink on water."
  - 52–75 s discovery: a padlocked hatch, knocking, "Hello? Is someone out there?"; dozens of kids "and grown men and women still wearing kid pajamas".
  - 75–84 s captured: "Another one for my collection… Tonight this boat sails out to sea for good."
  - 84–94 s twist: "the rule wasn't trapping us. The boat was. If this boat sat still on land for one hour, the ground would send every single person down here home."
  - 94–118 s climax: through a window; he steers the boat onto the beach ("Crunch") and throws the key in the lake; the clock runs 40… 50… 59… 60.
  - 118–137 s ending: everyone is spat home ("grown men climbing out of yards they hadn't seen in 30 years… Every single one of us home"). "And Mr. Mooney? Mr. Mooney ran, but to hide you have to stay in one place."
- **Twist:** the deadly rule becomes the rescue mechanism. Planted at 4–10 s (it spits you out at home). The last line turns the rule on the villain.
- **Ending:** Happy, with a **punchline loop** to the rule.
- **Tone:** Creepy (missing kids, the hatch) to triumphant. Warmth in the friend rescue.
- **Lore signals:** the creator commented "why do I always blow up 😂😂😂"; viewers say the premise is **copied from a "train" version** ("I already saw this but with a train", "This is copied").
- **Audio:**
  - **Voice:** a first-person kid narrator plus Max/Mooney lines, **~4.4 words/s**; pitch ≈ 196–220 Hz, low variation (5.6 semitones SD).
  - **Music:** a quiet continuous bed (bass −12 dB); **short drop-outs at 10.2, 21.2, 56.5 and 58.9 s** (beats around the "worms" gag and the knocking reveal).
  - **SFX:** hits at 8.3 s and 19.6 s (sinking/spit), 88.6 s, 106.9 s ("Crunch"), 116–118 s (the sinking at 60 min) and 132–133 s.
- **Captions:** lowercase chunks, white; diegetic MISSING posters with a red "MISSING" stamp.
- **Look:** Roblox avatars (a captain, kids in pyjamas, a grey-haired "Danny"); street, dock, boat, lake at night, beach. **About 131 cuts in 137 s (~1 s per shot), the fastest cutting of all 30 videos.**
- **Top 5 comments (~85 loaded):**
  1. @ashbash6122 (5,819): "I already saw this but with a train"
  2. @dylanstoriesyt (2,111, creator): "why do I always blow up 😂😂😂"
  3. @footballribs19 (2,018): (sticker/GIF, no text)
  4. @the__.w1nd (1,336): "ts is like the train story"
  5. @beanzybrow (509): "This is copied"
  - **Latch onto:** **originality** (a train version exists), creator banter.


## Answers

### 1. Which round-1 patterns also hold on YouTube Shorts?

Checked against the 12 YouTube hits (10 narrated plus 2 wordless game-lore animations). "Holds" means it appears on at least 3 YouTube channels.

| Round-1 pattern (Instagram) | On YouTube? | Evidence |
|---|---|---|
| First sentence = "In this world/town" + one rule | **Holds** (9 of 12) | ItsGuestCap, Gneef, RealDanty, Ryex, Gelo. Exceptions: JohnnyBoyRBX's second-person "You wake up…", and the two wordless Animal Hospital lore pieces. |
| Rule visible within ~2 s, often as a marker on people | **Holds** (9 of 12) | Numbers, words, price tags, glowing wrists, blue orbs, wrist buttons over/on every character (ItsGuestCap, Gneef, Ryex), plus giants (RealDanty) and a monster (Ryex). The low-view contrast Shorts are weaker here (L1 small device, L2 generic skull, L3 dark cameo crowd). |
| Quick 2–4-gag world-building montage up front | **Holds** | "Date night is just two people walking sideways" (Gneef), "One kid's word was banana" (ItsGuestCap), "Moms are worth millions. Babies are priceless" (Gneef), "The bus driver's son flattens his tires every night" (Gelo), Sky's helper examples (Ryex). |
| Protagonist is the exception to the rule | **Holds** | Zero lies / 1,528 lies (Y1), the word is "help" (Y5), an all-red family (Y4), Grandma worth $5 (Y6), born without Sky (Y9), two buttons used (Y11). |
| Climax turns the rule's own logic | **Holds** (≥6) | A red-blue human chain (Y4), "priceless" (Y6), the giant needs its sleeping human (Y8), the empty head is the safe place (Y9), the loophole in "accidental" (L2), the Robin Hood buttons (Y11). |
| Twist planted early | **Holds** (all narrated hits) | Tyler mocked then confessing (Y1), Theo avoided (Y4), "babies are priceless" (Y6), the doctor's "nothing in there" (Y9), flowers at the grave (Y12), "you don't see anything wrong in the mirror" (Y7). |
| Family/loved one at stake | **Holds** (8 of 12) | Little brother (Y1), Dad's first hug (Y4), Grandma (Y6), Dad (Y9), little brother and Mom (Y11), father/son (Y12), Mom (Y7), a lost family (Y3). |
| Last line echoes the opening | **Holds** | "nobody… ever hugged me" → the hug (Y4); "Lonely people… cheap" → "never be alone again" (Y6); "Hello, anyone in there?" → "Just me" (Y9); the forbidden word "help" left unsaid (Y5). |
| Fast cutting (a shot every ~1.2–2.3 s) | **Holds** | YouTube hits run 1.2–1.9 s per shot. |
| Comments go after loopholes / "what would I do" | **Holds, and stronger** | "Why not buy Mr puff" (16K), "How were his parent's 2 reds!?" (13K), "Just say give me infinite words"-style hacks on almost every hit. |
| First-person kid narrator | **Only partly** | Gneef, Ryex (sometimes) and Gelo use "I"; **ItsGuestCap, RealDanty and Ryex (Y10) narrate in third person**, and JohnnyBoyRBX uses "you". |
| One-word white captions ~70% down | **Only partly** | Gneef and RealDanty use single words. **ItsGuestCap, Ryex, Gelo and JohnnyBoyRBX use 2–6-word phrase blocks with CAPS and a red or coloured key word.** |
| Long (median ~106 s on Instagram) | **Shorter on YouTube** | Narrated YouTube hits run 54–162 s (median ~77 s); two of the biggest are 21–31 s wordless pieces. |

### 2. What's different on YouTube?

1. **Creators work their own comment sections.** In 8 of the 15 YouTube Shorts the creator's own comment sits in the top 5, almost always as a question or a game:
   - "How many lies do you think your number would show?" (Y1)
   - "What animal would you be?" (Y7)
   - "Part 2? Comment if you want part 2 or not." (Y10)
   - "Do you know what's 2+2?" (Y9)
   - "Why can nathan touch? Correct answer gets a heart!" (L2)
   - "Would you use your button to help a friend…" (Y11)
   - "what's a memory you'd replay forever?" (L1)
   - an off-topic "DROP HERE YOUR WILDEST RECIPES" thread (Y8)

   No round-1 Instagram hit had this.
2. **In-voice calls to action at the very end:** "And if you can hear me, too, like and subscribe" (Y9), "Like and subscribe or I'm your next kid" (Y12). The CTA is written into the story's last line.
3. **Explicit series hooks:** "Part 2?" asks, "Part 1" title cards (Y2), cross-video in-jokes (Ryex's "Verity/Falsity" meme dominates two of its comment sections), and shared names (Tyler is the bully in Y1 and Y9; "Dante" is RealDanty's recurring hero).
4. **Game-lore fan animation is a separate winning lane:** #2 and #3 by views are **wordless** 21–31 s animations about the Roblox game *Animal Hospital* (one is flat 2D, not Roblox-style). They run on music alone, and their comments are lore explanations.
5. **Third-person, adult-sounding narration is common**, and captions are more often phrase blocks with CAPS and a red key word.
6. **Many Instagram "accounts" are re-uploading YouTube Shorts.** Two direct matches:
   - **@robloxchiller's Instagram flop "WIND UP CREATURE" is RealDanty's YouTube Short** (identical video, posted a day later). It also underperformed on YouTube (177K vs RealDanty's 9–14M). The weakness is in the video, not the platform.
   - **@cipher_shorts' "Your Son Is Haunted" is Gelo Stories' YouTube Short** (identical; 9.6M on YouTube, 2.8M on Instagram).

   green_brorants' costume reel also ended with "subscribe if you enjoy my content", a YouTube-style CTA. **Some round-1 "accounts" are distributors, not creators**, so treat their success rates with care.
7. **Absolute numbers are bigger and engagement rates lower.** YouTube hits get 9.6M–36M views at ~1.5–3.5% likes per view; round-1 Instagram hits got ~5–8% likes per play.
8. **The contrast Shorts show the same weak spots as the Instagram flops:** an invisible rule (L1 replay device, L2 touch), no real cost or danger (L1), reused opening footage (L2 reuses Y10's intro), cluttered or confusing first seconds (L3), and no family stake (L2, L3).

### 3. What do the voices and music have in common across hits?

**Voices (measured):**
- **One main narrator carries every narrated hit.** Side characters get short quoted lines; on YouTube the transcript marks speaker changes in about half the hits (Y8, Y9, Y11, Y12). Y9 has a clearly separate female "Sky" voice.
- **Fast.** YouTube narrated hits run **3.9–5.2 words per second (median ~4.4)**, roughly 1.5× normal conversational speed (~2.5–3 w/s). The Instagram narration wasn't re-timed this round; round-1 caption counts suggested ~3–3.5 w/s there.
- **Mid-high pitch.** Voice-dominant medians cluster at **~180–240 Hz (median ~210 Hz)** on both platforms: a youthful, light voice, not a deep "movie trailer" one. Each channel keeps the **same voice profile across its videos** (ItsGuestCap ~200–250 Hz in Y1, Y5, Y11, L1; Gneef ~205 Hz in Y4, Y6).
- **Expressive but even.** Pitch spread is mostly 6–9 semitones. The flattest reads are dylanstoriesyt (4 st) and the cipher_shorts golf comedy (5 st).
- **AI or sped-up? Inference only.** Combined, the very high speed, the steady channel-wide pitch and the even delivery are **consistent with TTS or sped-up narration on most narrated hits**, but I can't confirm that without listening.

**Music (measured):**
- **A continuous bed under the narration in every narrated hit.** YouTube's transcript tags "[music]" 5–15 times per Short. It's mixed well under the voice: bass sits 5–25 dB below the voice band, and loudness is a uniform −16 to −19 dBFS (loud, compressed).
- **The most consistent music move: a sustained low drone/bass layer enters at the inciting moment or the turn, and stays to the end.** Seen in 8 hits across 5 accounts:
  - Gneef: ~25 s in both Y4 ("nobody in my house has ever hugged me") and Y6 ("I had five days…")
  - ItsGuestCap: ~28–32 s (Y1, Y5)
  - robloxstoriesdaily: 25 s (Magic Line)
  - craftee_films: 54 s and ~88 s (Steps, Never Turn Around)
  - noirfilmsanimations: ~88 s (Kevin)
- **Short silences for drama (YouTube):** 0.5–2 s near-silent gaps right before a reveal or turn, e.g. Y1 25.5–27.5 s (just before "1,528 times"), Y5 30.5–32.5 s (the turn), Y11 34–37.6 s ("He'd just keep walking"), Y7 3–4.5 s (after the hook). The five Instagram hits had **no** drop-outs, so silence is a tool some YouTube channels use, not a universal rule.
- **The wordless hits swap narration for a single song:**
  - Y2: one melodic track.
  - Y3: **switches from an upbeat bass-heavy track to a lone slow melody at exactly 10 s, the moment the story turns sad**.
  - capybluh's C1/C2: a sad-pop song with the strongest steady beat in the whole set.
- **Sound effects are sparse and tied to beats** (0–7 per hit), not to every cut, apart from an action-heavy climax (Y12: 14 hits in the storm and rescue). Comedy (cipher_shorts' golf story) does the opposite: almost no music and silent beats for timing.
