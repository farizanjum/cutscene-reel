---
name: cutscene-reel
description: Make a 25-35 second "game cutscene" product ad - a stylised 3D character wearing or holding the user's real product delivers a deadpan fun-fact rant on location, lands a punchline on the product, and cuts to the real product photo and URL. Use when the user asks for an AI character ad, a game-cutscene / PS2-style reel, a talking-character product video, "a video like the ones going viral with the game character in the t-shirt", or wants to turn a product photo into a short-form video ad for Instagram, TikTok or X.
---

# Cutscene Reel

Turn one product photo into a short talking-character ad in the "video game cutscene" format.

You are the director. The scripts do the generation; you make the creative calls, review every
frame sheet, and regenerate what is wrong. Most first takes need one or two fixes.

## What the format is

| Beat | Time | Shot | Job |
|---|---|---|---|
| Hook (optional) | 0-4 s | silent action | Stop the scroll: a small stylish action before any speech |
| Line 1 | 2-5 s | medium, gesture | A surprising "did you know" fact or an "it's funny how" observation |
| Line 2 | 3-5 s | wide, full outfit | Explain it. Shows the whole look and the location |
| Line 3 | 5-7 s | close-up | The joke. Sly, deadpan |
| Line 4 | 3-5 s | medium, points at product | The twist that lands on the product |
| End card | 3-4 s | real product photo | "get yours at <url>. link in bio." |

Rules that make it work: one character, one location, two-colour lighting taken from the product,
one dry voice at about 150 words a minute, a quiet lo-fi bed, white lowercase captions, a cut every
4-6 seconds, and the real product shown as a real photo at the end. Full breakdown:
`references/format.md`.

## Before you start

Ask the user for anything missing. Do not guess the product or the URL.

1. **Product**: 2-3 photos (one on a model or flat, one print close-up) and the URL for the end card.
2. **Character**: who is talking. Default to an original character you design. See "Rights" below.
3. **Location**: one place whose light matches the product's two main colours.
4. **Angle**: a true fact or an observation, and how it lands on the product.
5. **Keys**: `GEMINI_API_KEY` and `ELEVENLABS_API_KEY` in the environment or a `.env` file in the
   working folder. Never print keys or commit `.env`.

Needs Python 3 with Pillow (`pip install pillow`) and `ffmpeg` on the path.

## Pipeline

Work in a fresh project folder. `S` below is this skill's `scripts/` folder.

### 1. Script
Write 4 lines, 8-16 words each, plus the end-card line. Lowercase attitude, no hashtags, no hype.
Check every fact. Copy `examples/project.json` to `project.json` and fill in the lines.

### 2. Keyframes (one image per shot, 16:9)
```
python S/gen_image.py shots/k1_medium.png 16:9 "<prompt>" product/on_model.jpg product/print.jpg
```
- Make the **medium shot first**. Look at it. Fix it until the character and the product are right.
- Generate every other keyframe **from that image as the reference** ("same exact character, same
  location, new camera angle only"). This is what keeps the face the same across shots.
- Prompt templates for style, character, wide, close-up and pointing shots: `references/prompts.md`.

### 3. Animate
```
python S/make_shots.py project.json
```
Each shot becomes a 10 s clip with speech and lip-sync in `runs/<name>/out/`. Then for every clip:
```
python S/sheet.py runs/<name>/out/s1.mp4
```
and **read the sheet image**. Reject and regenerate (delete the .mp4, adjust the `action`, rerun) if:
- the face, skin tone or hair changes from the keyframe;
- the camera pushes in or cuts when it should hold;
- the product print turns to gibberish (common when the character moves away from camera).

### 4. Voice
```
python S/voice.py project.json
```
Transcribes each clip with word timestamps and converts the speech to one ElevenLabs voice with
speech-to-speech, which keeps the timing so lip-sync survives. Lines marked `CHECK` did not match the
script: read them, and regenerate the clip if words were dropped. Small transcript slips (a `?` for a
`.`, `47` for `forty-seven`) can be fixed by editing `out/sN_stt.json`, since captions are built from it.

### 5. Music
```
python S/music.py music/bed.mp3
```
Generates an original lo-fi bed. Set `"music"` in `project.json` to it.

### 6. Build
```
python S/build.py project.json
```
Trims each shot to its speech, crops to 4:3, upscales to 1440x1080, burns captions, adds the end
card, mixes voice over music. Output: `final/<name>.mp4`.

### 7. Check
```
python S/qc.py final/<name>.mp4
python S/sheet.py final/<name>.mp4 1
```
You cannot hear the video. `qc.py` has a model watch and listen and report voice consistency,
lip-sync, caption and continuity problems. Read it and the sheet, fix what they find, and tell the
user plainly what was checked by a model versus what they still need to watch themselves.

## The hook

A silent action shot before line 1 raises watch time. Add a shot with `"silent": true`, its own
`"prompt"`, and after reviewing its sheet a `"trim": [start, end]` and `"speed"` (1.5-1.75 works) so
it lands at 3-5 seconds. Examples that worked: applying lipstick, snapping the compact shut and
blowing a kiss at the lens; tossing a wrench, catching it and pointing it at camera. Keep the product
print out of frame or large in frame during fast motion, or it will smear.

## When a generation is blocked

Video models refuse some prompts. What has worked:
- **Third-party content block**: the keyframe shows a readable brand logo, or the wording names a
  brand. Reword the `action` without naming the garment, or use a keyframe where the logo is smaller.
  Retrying the same request sometimes passes.
- **Safety block**: soften physical-contact or suggestive wording (a kiss on the lens was blocked; a
  blown kiss toward the camera passed).
- **503 / high demand**: wait and rerun; finished clips are skipped.

## Using other models

The stages are independent. Swap any of them and keep the file contract:
- Keyframes: any image model that accepts reference images. Save `shots/<id>.jpg`.
- Animation: any image-to-video model that generates speech. Save `runs/<name>/out/<id>.mp4`.
  If the model has no speech, generate the line with text-to-speech and use a lip-sync model.
- Voice: any speech-to-speech and any transcriber that returns word timestamps in
  `{"words":[{"text","start","end","type":"word"}]}` as `out/<id>_stt.json`, voice as `out/<id>_vo.mp3`.
- `build.py` only needs those files plus `project.json`.

## Rights (read this before publishing)

- **Character**: design an original one. Do not recreate a recognisable character from a game, film
  or another creator's account, even "in the style of".
- **Product and brand**: only feature products and logos the user owns or has permission to use.
- **Music**: generate it or license it. Do not lift audio from someone else's video.
- **Facts**: verify them. A wrong "did you know" gets corrected in the comments.
- Tell the user if their request crosses one of these, and offer the clean alternative.
