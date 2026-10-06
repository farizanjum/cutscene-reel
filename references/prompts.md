# Prompt templates

Replace the parts in `<angle brackets>`. Keep the rest: the wording is what was found to work.

## Style block

Two looks have been tested. Pick one and paste it into every keyframe prompt.

**Retro (closest to the reference format)**
```
Rendering style: early-2000s Japanese action video game pre-rendered cutscene CGI (PlayStation 2 /
early PS3 era), stylised anime-realism 3D character model, slightly angular geometry, painted
textures, sculpted chunky hair strands, simple skin shader, strong coloured rim light, soft depth of
field. NOT photorealistic, NOT a photo, NO black outlines, NO 2D illustration.
```

**Modern (cleaner, reads as a current game)**
```
Rendering style: stylised 3D video game character CGI, smooth shaded 3D geometry, painted textures,
strong coloured rim light, soft depth of field. NOT photorealistic, NO black outlines, NO 2D
illustration, NO cel shading.
```

## Keyframe 1: medium shot (make this first)

References to pass: product on-model photo, product print close-up.
```
<STYLE BLOCK> Create an ORIGINAL character, not any existing game or film character:
<age, build, face, attitude>. Hair: <hair>. <head accessory>. <gloves / jewellery / belt / trousers>.
They wear EXACTLY the <product> from the reference photos (<colour, print, logo placement>) -
reproduce the print faithfully and clearly visible.
Location: <place> at <time of day>, <two-colour light description>. Colour palette strictly
<colour A> and <colour B>.
Shot: medium waist-up, leaning on <railing / wall / car>, index finger raised making a point,
mid-sentence, playful smug expression. No text, no captions, no watermark. 16:9 frame.
```

## Other keyframes (pass keyframe 1 as the first reference)

Start each with:
```
Same exact 3D CGI character as the first image (same face, same skin tone, same hair, same outfit,
the same <product> with the print clear and accurate), same location, same lighting and rendering
style. New camera angle only. No text. 16:9 frame.
```
Then add one of:

- **Wide**: `Shot: wide full-body. They lean back against <object> with both arms spread in a relaxed shrug; the whole outfit and the location are visible.`
- **Close-up**: `Shot: tight low-angle close-up of the face and shoulders, head tilted, one eyebrow raised, sly closed-mouth smirk, looking into the camera, background lights blurred into bokeh.`
- **Point**: `Shot: medium waist-up, facing camera, smirking and pointing a thumb at the print on their own <product>; the print is the hero of the frame.`
- **Hook**: `Shot: medium close-up, three-quarter view, <prop action that can be held as a still, e.g. applying lipstick in a compact mirror / holding a wrench at an open car hood>.`

Changing one detail of an existing keyframe: `Edit this image: change ONLY <thing>. Everything else stays exactly the same.`

## Animation (`project.json`)

`voice_direction`
```
dry, wry, slightly smug young American <woman's / man's> voice, General American accent, casual internet-creator cadence, medium-fast pace
```
`style`
```
3D video game cutscene. Subtle handheld camera drift. Accurate lip sync. No music, no subtitles, no on-screen text. They finish the line, then hold a smirk in silence.
```
`action` per shot (the script appends `in a <voice_direction>: "<line>"`):
- `The <woman / man> raises an index finger and says`
- `Static locked-off wide shot, the camera does not move or zoom and they stay full-body in frame with the same face throughout. They shrug with open palms and say`
- `Close-up. They tilt their head and say with a sly grin`
- `They smirk at the camera, tap their chest with a thumb, and say`

Silent hook shot (`"silent": true`, full `"prompt"`):
```
Animate this image into a video with synchronized audio. 3D video game cutscene. <Action in three
beats, ending on a look to camera that is held>. Snappy, stylish. Subtle camera push-in. Only sound
effects: <two sounds>. No speech, no music, no subtitles, no on-screen text.
```
Add `The camera stays on a close-up of the face and shoulders the whole time.` if the product print
smears, and `NO graphics or effects appear anywhere on screen.` if the model adds overlays.

## Music

```
Instrumental only, no vocals. Mellow lo-fi chill hip-hop beat, 86 BPM, warm electric piano chords,
soft sub bass, relaxed boom-bap drums with closed hi-hats, vinyl warmth, 40 seconds.
```

## Script patterns

- `did you know <true surprising fact>?` -> `<one-sentence detail>.` -> `like, imagine being <someone affected by it>. <absurd consequence>.` -> `anyway. <pivot that lands on the product>.`
- `it's funny how <thing everyone has noticed>.` -> `<three short examples>.` -> `and it still <fails at the basic thing>. <the old thing> <just works>.` -> `some things you just don't upgrade. like this <product>.`
