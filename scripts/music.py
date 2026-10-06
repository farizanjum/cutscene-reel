"""music.py OUT.mp3 ["PROMPT"]

Generate an original instrumental music bed with Lyria.
Do not lift the music from someone else's video: generate a bed or use a track you have licensed."""
import base64, sys
from common import key, post_json

out = sys.argv[1] if len(sys.argv) > 1 else 'music.mp3'
prompt = sys.argv[2] if len(sys.argv) > 2 else (
    'Instrumental only, no vocals. Mellow lo-fi chill hip-hop beat, 86 BPM, warm electric piano chords, soft sub bass, '
    'relaxed boom-bap drums with closed hi-hats, vinyl warmth, laid-back streetwear ad background music, 40 seconds.')
body = {'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'responseModalities': ['AUDIO']}}
for model in ('lyria-3.5', 'lyria-3-clip-preview'):
    r, err = post_json(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
                       body, {'x-goog-api-key': key('GEMINI_API_KEY')}, 600)
    if err:
        print(model, err)
        continue
    for p in r.get('candidates', [{}])[0].get('content', {}).get('parts', []):
        d = p.get('inlineData')
        if d:
            open(out, 'wb').write(base64.b64decode(d['data']))
            print('OK', out, model)
            sys.exit(0)
sys.exit('No audio returned')
