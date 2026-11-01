# blocky-stories

[Privacy Policy](PRIVACY.md) · [Terms of Service](TERMS.md)

Made-up creepy stories told by a fast narrator over blocky characters built in Blender, for PandaNanoAdventures.

```
stories/<name>/        script.md, story.json, set.py, voice-timings.json, package.json, reviews/
blocky/                the engine: characters, sets, voice, edit, captions, sound, checks, flash measure
.github/workflows/     test, render (final films on free runners), upload (daily, private)
RULES.md               the house rules
docs/                  engine reference, YouTube setup, the owner's reference short
```

```bash
bash blocky/setup.sh                       # once: Blender (bpy) and TTS venvs; export what it prints
python -m blocky voice <story>             # narrate (Kokoro), keep word timings
python -m blocky preflight <story>         # every automatic check, one summary
python -m blocky stills <story> --t 1.5,12 # look-dev frames
python -m blocky render <story> --preview && python -m blocky finish <story> --preview && python -m blocky mix <story> --preview
python -m blocky gate <story>              # ready to ship?
python -m pytest -q
```

The final render, flash measure and upload happen on GitHub Actions after merge.

Font: Schibsted Grotesk (SIL OFL 1.1, `blocky/fonts/OFL.txt`). Narrator: Kokoro-82M (Apache 2.0).

**Policies:** [Privacy Policy](PRIVACY.md) · [Terms of Service](TERMS.md). The uploader acts only on the owner's own channel through the YouTube API Services.
