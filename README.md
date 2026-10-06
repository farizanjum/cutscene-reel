# cutscene-reel

An agent skill that turns one product photo into a 25-35 second "game cutscene" ad: a stylised 3D
character wears your product, delivers a deadpan fun-fact rant on location, lands the punchline on
the product, and cuts to the real product photo and your URL.

## Install

Get the zip from https://lowballknowledge.vercel.app and unzip it into your agent's skills folder.

- **Claude Code**: `~/.claude/skills/cutscene-reel`
- **Any other agent** (Cursor, Codex, Gemini CLI...): unzip it anywhere and tell the agent
  `Read SKILL.md in ./cutscene-reel and follow it.`

## Use

Put two or three product photos in a folder, add your keys, and ask:

> Use the cutscene-reel skill. Product photos are in ./product. Make a reel for
> www.mybrand.com with a female character on a rooftop in Tokyo at night.

## Needs

- Python 3 with Pillow (`pip install pillow`) and `ffmpeg`
- `GEMINI_API_KEY` (keyframes, animation with speech, music, QC)
- `ELEVENLABS_API_KEY` (one consistent voice, word timestamps for captions)

Any stage can be swapped for another model; `SKILL.md` lists the file contract.

## What's inside

| Path | What |
|---|---|
| `SKILL.md` | The workflow the agent follows |
| `references/format.md` | The format decoded: structure, shots, voice, music, captions |
| `references/prompts.md` | Prompt templates for keyframes, animation, hook, music, scripts |
| `examples/project.json` | A filled-in project file |
| `scripts/` | `gen_image` `make_shots` `voice` `music` `build` `qc` `sheet` |

## Use it responsibly

Design your own character, feature only products and logos you have the right to use, generate or
license your music, and check your facts. The skill tells the agent the same.

MIT licence.
