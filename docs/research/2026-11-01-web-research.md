# Research: deeper creepy blocky stories for PandaNanoAdventures

Date: 2026-11-01. Labels used: **[E]** means a source says so (URL given). **[I]** means it's my own inference. Most sources on Shorts "algorithms" are vendor blogs. YouTube publishes no weights, so I mark those as vendor opinion.

Access note: support.google.com and buffer.com wouldn't load from this session (blocked by the network allowlist), so YouTube Help pages are cited through search snippets and press coverage. GitHub READMEs were read directly.

---

## Top 10 things to change in our pipeline, ranked by expected impact

1. **Test shorter cuts (75 to 100 s) against the 2:15 to 2:30 house length.** YouTube has published no reach penalty for 1 to 3 minute Shorts, and promised to improve how it recommends them [E: https://support.google.com/youtube/answer/15424877]. But every source agrees that a long Short only wins if it holds people, and the one creator survey found sub-60 s videos break through most often [E: https://www.adobe.com/express/learn/blog/youtube-shorts-length-study, self-reported]. Back-row got about 15K engaged views from about 24.8K views. [I] That suggests strong first-seconds pull, then losses we can't see yet. Write 2 of every 7 stories at 90 s, and change RULES.md's length rule only if the data says so.
2. **Pull our real retention curve into `metrics.yml`.** The YouTube Analytics API returns `audienceWatchRatio` by `elapsedVideoTimeRatio` (100 points), plus `relativeRetentionPerformance` against videos of similar length [E: https://kiwix.lema.org/stackoverflow.com_en_all_2023-11/questions/40345970/youtube-analytics-api-v3-retrieving-relative-audience-retention; https://tube2sheetdocumentation-2tv.pages.dev/queries-guide/youtubeAnalyticsApi/audience-retention-for-a-video]. It's free and uses the same OAuth as upload. Map each drop onto our line IDs (L03, L07 and so on), so the writer learns which kind of beat loses people. Effort: about 1 day.
3. **Move the character rig further from Roblox's classic R6 avatar.** Roblox's Terms of Use bar off-platform commercial use of "derivatives of the classic Roblox avatars" (R6/R15). Roblox also says it still allows videos made with avatars [E: https://devforum.roblox.com/t/update-to-roblox-licensing-program-brand-guidelines/1843674; https://en.help.roblox.com/hc/articles/115001708126]. Our `rig.py` is literally "R6-style: box torso 2 x 2 x 1, arms and legs 1 x 2 x 1". [I] That's the one IP exposure left after RULES.md rule 4. Change at least two signature proportions (head shape or size, limb ratio, a visible joint or hands) so the character reads as "blocky" and not as a copy of R6. Effort: half a day, plus a look test with the owner.
4. **Add a "rules" story mode with a contradiction ("kick").** Rule-based creepypasta works when it has many rules, never states the penalty for failing, and has two rules that contradict each other [E: https://112s.substack.com/p/neapolitan-rule-creepypasta]. This fits our "strange rule in the first two seconds" hook, and it makes people comment ("which rule would you break?"). Effort: writer prompt only.
5. **Make lore visible across episodes: numbered entries and Part 2s.** Analog horror and the Backrooms grew by handing out lore in fragments viewers piece together, with restraint and no "one true canon" [E: https://bloody-disgusting.com/editorials/3958525/the-mandela-catalogue-explained-inside-alex-kisters-viral-analog-horror-phenomenon/; https://frayedbranches.substack.com/p/how-the-backrooms-can-fix-internet; https://theghostinmymachine.com/2022/02/14/the-weird-part-of-youtube-unraveling-the-story-and-universe-of-backrooms-found-footage/]. `lore.md` already exists, but its links are hidden. [I] Also add one *visible* series device: a recurring object, or a "Rule #N" title number. When a story outperforms, give it a follow-up instead of always making a new world. RULES.md rule 5 still holds, because a Part 2 has a new set and a new twist.
6. **Build a free competitor tracker.** Use the YouTube Data API (10,000 units a day; `videos.list` costs 1 unit for up to 50 IDs, `search.list` costs 100) [E: https://developers.google.com/youtube/v3/determine_quota_cost; https://outlierkit.com/resources/youtube-api-quota/] together with yt-dlp (Unlicense, https://github.com/yt-dlp/yt-dlp) for metadata only. Pull 20 to 30 niche channels' Shorts each week and flag outliers (views ÷ channel median). Log their title pattern, length and opening line. Effort: about 1 day. This also fills the gap below: I couldn't find reliable public numbers for the niche's channels.
7. **Make the twist rewatchable on purpose, and point the pin at the plant.** Use the "surprising yet inevitable" test: clues you can only read in hindsight, plus a red herring [E: https://nathanbaugh.substack.com/p/story-twists; https://screenwritingmagazine.com/2016/06/28/make-climax-feel-inevitable-not-predictable/amp/]. A narrative loop, where the ending reframes the opening, is the creator-recommended loop shape [E: https://faceless.so/blog/looping-short-videos-tutorial-story-seamless-loops, vendor]. Our rules already require this. [I] The upgrade is to make the critic check it: list the two plant timestamps and confirm each one is on screen for at least 1 s.
8. **Richer acting from free motion libraries.** Quaternius Universal Animation Library 1 and 2 have 250+ CC0 clips (check each pack, since newer packs use the "Quaternius Asset Licence") [E: https://app.cinevva.com/guides/free-character-animations-rigging]. CMU mocap BVH data is free for commercial use but needs cleanup [E: https://www.roboticscenter.ai/datasets/cmu-mocap/; https://groups.google.com/g/bvhacker/c/r906SGjjcTA]. Retarget a handful of these (crouch, flinch, crawl, peek, stumble) onto our rig in `acting.py`. Effort: 2 to 4 days. [I] Today our scares come from the camera and effects. Body language is the cheapest way to add more fear.
9. **Reply to comments early, and stop asking directly for them.** Vendors disagree on whether a direct "comment below" helps on Shorts. Several say debate prompts and creator replies matter more [E: https://subscribr.ai/youtube-strategy/scripting-youtube-shorts-engagement; https://fluxnote.io/guides/youtube-comment-section-strategy-2026, vendor opinion]. [I] Add to the owner's upload issue: "reply to the first 5 comments within 1 hour" and "pin the best theory".
10. **Captions: force-align to the known script.** stable-ts aligns plain text to audio at word level and has a faster-whisper backend. It's MIT licensed but archived [E: https://github.com/jianfch/stable-ts]. It removes ASR wording errors from the Whisper check. Kokoro already gives token timings, so this is a robustness fix, not a visible one. Effort: half a day.

Not in the top 10: switching TTS (see 3b). Cross-posting to Instagram is the owner's call (see 1f).

---

## 1. What makes creepy Roblox-style story Shorts succeed

**a. The channels. Evidence is weak here.** I couldn't find reliable press, Social Blade or vidIQ data for the specific "creepy Roblox story Short" accounts. Search results were dominated by SEO spam pages. What I could verify:
- Story-driven Roblox channels: **Poke**, about 5.3M subscribers and 1.4B views. **Hyper – Roblox**, about 2.3M subscribers and 665M views, uploads daily and is "mostly story-based" [E: https://influencermarketinghub.com/roblox-youtube-channels/].
- **Noob Roblox Story**, about 799K subscribers (Nov 2024 snapshot) [E: https://vidiq.com/youtube-stats/channel/UC4baMLPRs1iG9mvOpxVYaVw].
- **ItsFunneh**, about 11.6M subscribers, voice-acted Brookhaven skits that include haunted plots [E: https://www.maxpowergaming.co/post/top-ten-roblox-youtubers-with-100-million-subs-combined].
- **Robypolarbear** passed 1M subscribers by May 2023 with narrated Roblox stories (long-form) [E: https://en.wikipedia.org/wiki/Robypolarbear].
- Non-Roblox animated horror with a narrator: **Llama Arts** (about 2.5M) [E: https://creatordb.app/creatorstats/llamaarts/] and **Wansee Entertainment** (about 1.49M) [E: https://www.tbsnews.net/node/510114].
- [I] The fast, sped-up TTS "creepy Roblox story" Shorts accounts seem to be newer and mostly faceless, and nobody has written about them. Item 6 above is how we get real numbers.

**b. Craft patterns from creepypasta, the closest studied form.** In a read of the 72 most-shared creepypastas, 68% were first person. Common ingredients were cliffhanger endings, unexplained phenomena and monsters [E: https://venngage.com/blog/creepypasta/; coverage: https://www.inverse.com/article/16672-a-new-study-on-creepypasta-demonstrates-how-to-make-your-internet-fiction-go-viral]. This sample was picked by popularity, so it shows correlation and doesn't prove what makes a story spread.

**c. Shorts distribution, 2025 to 2026.**
- **Viewed vs swiped away** is the first filter creators watch. YouTube's Shorts lead Todd Sherman said not every swipe counts as a view, that thresholds are kept private to stop gaming, and that some systems find a Short a "seed audience" and can then stall [E: https://www.searchenginejournal.com/youtube-explains-how-shorts-algorithm-works/494953/]. The 70 to 80% "viewed" targets are vendor rules of thumb [E: https://subscribr.ai/youtube-strategy/youtube-shorts-analytics-metrics-viral].
- **Views vs engaged views:** since 31 March 2025, a view counts on every start or replay. The old metric is now "engaged views", and YPP revenue uses engaged views [E: https://ppc.land/youtube-changes-how-shorts-views-are-counted-from-march-31/]. [I] Our 15K engaged out of 24.8K means about 40% of starts didn't reach the engaged threshold.
- **Loops:** replays count as views [E: same]. Creators match the last frame to the first, or use a sentence that continues across the loop point [E: https://vidiq.com/blog/post/double-youtube-watch-time-looping-shorts].
- **Comments and shares:** said to be high-weight. That's vendor opinion, with no YouTube numbers [E: https://subscribr.ai/youtube-strategy/scripting-youtube-shorts-engagement].
- **2 to 3 minute Shorts:** allowed since 15 Oct 2024. YouTube said it would improve recommendations for them [E: https://9to5google.com/2024/10/03/youtube-shorts-3-minutes/; https://support.google.com/youtube/answer/15424877]. I found **no published evidence of a penalty**, only vendor warnings that 1:01 to 3:00 "might struggle" and the creator survey [E: https://piktochart.com/blog/how-long-youtube-shorts/; Adobe above]. A 1 to 3 minute Short with Content ID-matched music gets blocked, which doesn't affect us because our audio is all synthesized [E: https://9to5google.com/2024/10/03/youtube-shorts-3-minutes/].

**d. Titles and series.** I found no solid data specific to the niche. [I] Use a rule or premise as the title ("In this town, nobody looks up"), which matches the owner's reference, and use numbering for a series.

**e. Instagram Reels, the owner's belief.** It's partly supported. Mosseri's named Reels signals are watch time, likes per reach and sends per reach. Sends (DM shares) matter most for reaching non-followers [E: https://creatorflow.so/blog/instagram-algorithm/, secondary]. A lore or twist story that people send to a friend ("watch till the end") fits sends per reach. That part is [I]. Reels can run up to 3 minutes, and Reels over 3 minutes reportedly fall outside recommendations to non-followers [E: https://miraflow.ai/blog/3-minute-reels-2026-when-longer-reels-beat-short-reels, unverified against Instagram]. Trial Reels show a Reel to non-followers first, and need 1,000 followers and a public account [E: https://www.thekeyword.co/news/instagram-expands-trial-reels-to-all-public-creators-with-1k-or-more-followers]. I found no study specific to lore or twist stories on Reels.

**f.** Cross-posting to Instagram would be a second platform for the same video. That's for the owner to decide, since the "no video on two channels" rule was written about YouTube channels.

---

## 2. Story craft we can turn into rules (11 techniques)

1. **Rules with no stated penalty.** Let the viewer imagine the cost [E: https://112s.substack.com/p/neapolitan-rule-creepypasta].
2. **Two rules that contradict.** The "kick" is the moment the narrator can't obey both [E: same].
3. **Rules that feel older than the narrator.** The logic predates them and outlasts their failure [E: https://tvtropes.org/pmwiki/pmwiki.php/SoYouWantTo/Creepypasta].
4. **Two-sentence shape for every beat.** Setup line, then a pivot line, with the second line shorter [E: https://www.pupperish.com/short-horror-stories; https://www.finaldraft.com/blog/two-sentence-horror-stories]. [I] Our beats are already one sentence, so pair them as setup and pivot.
5. **Lost time.** The narrator can't account for minutes, hours or days [E: https://springhole.net/writing/better-creepypasta-and-horror-characters.htm].
6. **Lore as fragments, never explained in full.** Leave a gap for viewers to argue about in the comments [E: https://bloody-disgusting.com/editorials/3958525/the-mandela-catalogue-explained-inside-alex-kisters-viral-analog-horror-phenomenon/; https://frayedbranches.substack.com/p/how-the-backrooms-can-fix-internet].
7. **In-world "official" artefacts.** Analog horror uses fake emergency notices and broadcasts to build its world [E: https://bloody-disgusting.com/editorials/3958525/the-mandela-catalogue-explained-inside-alex-kisters-viral-analog-horror-phenomenon/]. [I] For us that means a made-up-language notice board or a siren pattern that recurs across stories. RULES.md rule 1 still bans real-world text.
8. **Escalate through small changes to the same frame.** Local 58 escalates by changing title cards, without budget effects [E: https://www.dreadcentral.com/editorials/439064/analog-horror-and-its-blueprints-for-horrors-future, opinion]. [I] Reuse one shot three times and move one thing each time.
9. **Surprising yet inevitable twists.** Plant clues you can only read in hindsight (a recurring object, a throwaway line, an odd behaviour) and add one red herring. Don't overexpose them [E: https://nathanbaugh.substack.com/p/story-twists; https://www.editorworld.com/article/how-to-write-a-plot-twist].
10. **A narrative loop.** The last line causes or reframes the first, so the replay plays as a new scene [E: https://faceless.so/blog/looping-short-videos-tutorial-story-seamless-loops, vendor].
11. **Named characters with personalities, even inside the mystery.** Kane Pixels' Backrooms grounds its lore in people [E: https://frayedbranches.substack.com/p/how-the-backrooms-can-fix-internet].

Deeper free reading: Joe Ondrak's thesis "Digesting creepypasta" (Sheffield Hallam, 2022) [E: https://shura.shu.ac.uk/32027], and a Georgia Tech thesis on The Mandela Catalogue [E: https://repository.gatech.edu/entities/publication/b26e1f62-2b28-4c91-bbf8-b980031ea435].

---

## 3. Tools to reuse or rebuild (free and open source)

### a. Blender: characters, rigging, animation
| Tool | Licence | What it adds for us | Effort |
|---|---|---|---|
| Rigify (ships with Blender; `bpy.ops.pose.rigify_generate`) https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/addons/rigify/basics.rst | GPL (Blender) | Real IK and FK on our blocky body, which makes retargeting mocap possible | Med. [I] Only worth it if we do item 8 |
| Quaternius UAL 1 and 2, Ultimate Animated Characters https://app.cinevva.com/guides/free-character-animations-rigging | CC0 for older packs; newer packs use QAL v1.0 (commercial OK, no resale) | 250+ animation clips to retarget | Med |
| CMU Motion Capture (BVH) https://www.roboticscenter.ai/datasets/cmu-mocap/ | Free for commercial use (one repackage says CC-BY 4.0, so check) | Natural crawl, stumble and cower moves | Med-High (joint flips) |
| Kenney and KayKit animated characters (same guide) | CC0 | Reference only. Don't use them as our cast, because of brand consistency | Low |
| ProcFunc https://github.com/princeton-vl/procfunc | see repo | Converts Geometry Nodes into Python, useful for procedural sets | Med |

Mixamo is free to use but isn't open source (Adobe terms) [E: cinevva guide above]. [I] Leave it out under the $0 open-source rule. I found no maintained open-source "blocky character generator". Our `rig.py` already is one.

### b. TTS (alternatives to Kokoro-82M)
| Model | Licence | Notes | Verdict |
|---|---|---|---|
| Kokoro-82M (current) https://github.com/hexgrad/kokoro | Apache-2.0 weights | `speed` parameter, token timings, fast on CPU | Keep as the default |
| Chatterbox Turbo (350M) / Nano (110M) https://github.com/resemble-ai/chatterbox | MIT | `exaggeration` control for a more dramatic delivery (higher values also speed up speech). Nano runs about 3x realtime on 8 CPU cores. **Every file carries the Perth watermark** | Best candidate for a more expressive narrator. Run a look test with the owner |
| Zonos https://github.com/Zyphra/Zonos | Apache-2.0 | Emotion control (fear) and speaking rate. Needs 6 GB+ VRAM, slow on CPU | Too heavy for CI |
| Supertonic https://github.com/supertone-inc/supertonic | Code MIT, weights OpenRAIL-M (commercial use allowed, with use restrictions) | Very fast on CPU, 66 to 99M parameters. Repo is archived | A speed option only |
| KittenTTS https://github.com/KittenML/KittenTTS | Code Apache-2.0. KittenTTS 2 weights are under the Stellon "Community License" | Tiny ONNX models of 15 to 80M parameters. v2 adds emotions | Check the weight licence before any use |
| CosyVoice2, Dia, Sesame CSM https://tts.ai/blog/open-source-text-to-speech-guide-2026/ | Apache-2.0 (vendor table) | Expressive, but larger or slower | Low priority |

[I] The voice is part of the brand (owner, 2026-10-30), so any swap needs the owner's look test. Speed isn't our bottleneck. If we change anything, the reason should be expressiveness.

### c. Word-level caption timing
- **stable-ts** https://github.com/jianfch/stable-ts (MIT, archived): `align()` of known text to audio, with a faster-whisper backend. It replaces ASR-based checking. Effort: low.
- **WhisperX** https://github.com/m-bain/whisperX (MIT per aggregators): wav2vec2 forced alignment. Numbers and symbols can drop their timestamps [E: https://www.sourcepulse.org/projects/1473319]. Effort: low.
- Kokoro's own token timings are the most exact source for sped-up audio. [I] Scale them by our tempo factor and use the aligner only as a cross-check.

### d. "Shorts factory" pipelines
| Repo | Licence | What it does | What we could borrow |
|---|---|---|---|
| short-video-maker https://github.com/gyoridavid/short-video-maker | MIT | Kokoro, whisper.cpp captions, Pexels footage, Remotion | Its MCP and REST pattern. Nothing visual (stock footage is exactly the "inauthentic" risk) |
| MoneyPrinterTurbo https://github.com/harry0703/MoneyPrinterTurbo | MIT | Topic, script, TTS, footage, subtitles, upload. Subtitles come either from TTS timestamps or from faster-whisper | Its config switch between the two subtitle sources. Note its bundled music comes from YouTube, so never reuse that |
| ShortGPT https://github.com/RayVentura/ShortGPT | MIT | An LLM-readable "editing markup" built on MoviePy | Its idea of a JSON edit language. Our `story.json` is already richer |

[I] These are all stock-footage-plus-TTS factories, the exact pattern YouTube names as inauthentic. Our own-built 3D world is the main thing that sets us apart. Borrow plumbing from them, never format.

### e. Competitor analysis
- YouTube Data API v3: 10K units a day free [E: https://developers.google.com/youtube/v3/determine_quota_cost]. Use `channels.list`, then `playlistItems.list` on the uploads playlist, then `videos.list` (1 unit each) instead of `search.list` (100).
- yt-dlp https://github.com/yt-dlp/yt-dlp (Unlicense): metadata JSON (duration, title, view count) without downloading.
- YouTube Analytics API (our own channel only): retention curves, as in top-10 item 2.
- Competitors' retention isn't public. [I] Use views ÷ subscribers outliers and comment counts as proxies.

---

## 4. Risks

**Inauthentic or mass-produced content (YPP).** On 15 July 2025 YouTube renamed "repetitious content" to "inauthentic content". It called this a minor clarification, applied whether or not AI is used, and the penalty is loss of monetization, not removal [E: https://www.plagiarismtoday.com/2025/07/08/youtube-targets-inauthentic-content/; https://www.netinfluencer.com/youtube-clarifies-july-15-policy-update-repetitious-content-rebranded-as-inauthentic-content/]. The named example: channels uploading **narrated stories with only superficial differences** [E: https://theprint.in/world/youtube-cracks-down-on-inauthentic-content-with-monetisation-policy-update-what-new-guidelines-say/2691562]. In January 2026 Neal Mohan named "managing AI slop" a priority. Days later, about 16 to 18 of the top AI-slop channels were terminated or emptied [E: https://tubefilter.com/2026/01/29/youtube-ai-slop-channel-crackdown-bans/]. One outlet argues faceless creators are being caught in this, which is unconfirmed [E: https://www.webpronews.com/youtubes-war-on-ai-slop-collides-with-faceless-creators-who-built-the-platform-first/].

[I] What keeps us safe:
- **Visible differences between stories:** a new set, cast, creature and twist each time. RULES.md rule 5 and `check` already enforce this.
- **A human in the loop**, recorded: the owner's look test and final watch.
- **No stock footage or templated slideshows.**
- **The synthetic voice is the main sameness signal.** Keeping it consistent is a brand choice, so vary pacing, music and sound design per story.
- **Don't scale past one a day.**
- Synthetic-content disclosure covers *realistic* altered content. Animated fiction doesn't need it [E: https://www.plagiarismtoday.com/2025/07/08/youtube-targets-inauthentic-content/]. That matches our current "No".

**Roblox IP.** No Roblox name or logo in commercial content. Roblox doesn't grant unsolicited commercial requests [E: https://en.help.roblox.com/hc/articles/115001708126]. Derivatives of the classic R6/R15 avatars are restricted off-platform [E: https://devforum.roblox.com/t/update-to-roblox-licensing-program-brand-guidelines/1843674]. See top-10 item 3.

**Made for kids.** YouTube lists animated or cartoon characters as an indicator that content is made for kids, but says one factor alone doesn't make a video made for kids [E: https://support.google.com/youtube/answer/9528076]. The FTC accepts that animation can appeal to everyone [E: https://vidiq.com/blog/post/is-your-youtube-content-made-for-children-ftc-coppa/]. YouTube removes mature or violent content that *targets* kids through its title, description or tags. That rule doesn't apply to animation clearly aimed at adults [E: https://news.slashdot.org/story/19/08/23/2218212/youtube-says-it-will-now-remove-violent-and-mature-videos-pretending-to-be-kid-friendly]. The amended COPPA rule's compliance date was 22 April 2026 [E: https://ppc.land/youtubes-coppa-deadline-hits-what-the-audience-setting-rules-really-mean/]. [I] Our current setup is the right one: `made_for_kids=false`, no kid-aimed words, no children in the cast, no gore. Add one more thing: keep the thumbnail frame and the first shot from looking like a toddler cartoon. Use dark grading and adult characters.
