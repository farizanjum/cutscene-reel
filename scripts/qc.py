"""qc.py final/video.mp4

Ask a Gemini model to watch and listen to the finished cut and report problems.
An agent cannot hear the video, so run this and read it before calling the video done."""
import base64, os, sys
from common import key, post_json

MODEL = os.environ.get('QC_MODEL', 'gemini-3.8-flash')
Q = """You are a strict QC reviewer for a short social video ad. Watch and listen carefully. Report concisely:
1. Verbatim transcript with timestamps.
2. Voice: ONE consistent speaker across all shots? Natural or robotic? Glitches, clipped words, odd pronunciations (timestamps)?
3. Lip-sync accuracy per shot (good / slightly off / bad).
4. Captions: any caption that mismatches the speech, is mistimed, overflows, or is hard to read (timestamps).
5. Music: level against the voice, abrupt starts or stops.
6. Visual: character consistency between shots (face, skin tone, hair, outfit, product print), morphing or artifact frames, garbled text on clothing, bad cuts (timestamps).
7. Overall score out of 10 and the top 3 fixes."""

b = base64.b64encode(open(sys.argv[1], 'rb').read()).decode()
r, err = post_json(f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent',
                   {'contents': [{'parts': [{'inline_data': {'mime_type': 'video/mp4', 'data': b}}, {'text': Q}]}]},
                   {'x-goog-api-key': key('GEMINI_API_KEY')}, 600)
if err:
    sys.exit(err)
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
print(''.join(p.get('text', '') for p in r['candidates'][0]['content']['parts']))
