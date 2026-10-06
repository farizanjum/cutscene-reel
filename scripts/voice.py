"""voice.py project.json

For every speaking shot: extract the clip's audio, get a word-level transcript (ElevenLabs Scribe),
and convert the speech to the project's voice with speech-to-speech, which keeps timing and lip-sync.
Also makes the end-card line with text-to-speech in the same voice. Existing files are skipped."""
import json, os, subprocess, sys, urllib.request, urllib.error, uuid
from common import key, project

P = project()
OUT = P['dir'] + '/out'
V = P['elevenlabs_voice_id']
KEY = key('ELEVENLABS_API_KEY')
VS = json.dumps(P.get('voice_settings', {'stability': 0.5, 'similarity_boost': 1.0, 'style': 0.2, 'use_speaker_boost': True}))


def post(url, fields=None, files=None, body=None):
    if body is not None:
        data, ct = json.dumps(body).encode(), 'application/json'
    else:
        bd = uuid.uuid4().hex
        parts = []
        for k, v in (fields or {}).items():
            parts.append(f'--{bd}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
        for k, p in (files or {}).items():
            head = f'--{bd}\r\nContent-Disposition: form-data; name="{k}"; filename="{os.path.basename(p)}"\r\nContent-Type: audio/wav\r\n\r\n'
            parts.append(head.encode() + open(p, 'rb').read() + b'\r\n')
        data, ct = b''.join(parts) + f'--{bd}--\r\n'.encode(), f'multipart/form-data; boundary={bd}'
    try:
        return urllib.request.urlopen(urllib.request.Request(url, data=data, headers={'xi-api-key': KEY, 'Content-Type': ct}), timeout=300).read()
    except urllib.error.HTTPError as e:
        sys.exit(f'HTTP {e.code} {url} {e.read().decode(errors="replace")[:400]}')


def norm(t):
    return ''.join(c for c in t.lower() if c.isalnum())


for s in P['shots']:
    if s.get('silent'):
        continue
    b = f"{OUT}/{s['id']}"
    if not os.path.exists(b + '.mp4'):
        print(s['id'], 'missing clip')
        continue
    if not os.path.exists(b + '_raw.wav'):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', b + '.mp4', '-vn', '-ac', '1', '-ar', '44100', b + '_raw.wav'], check=True)
    if not os.path.exists(b + '_stt.json'):
        open(b + '_stt.json', 'wb').write(post('https://api.elevenlabs.io/v1/speech-to-text',
                                               {'model_id': 'scribe_v1', 'timestamps_granularity': 'word', 'language_code': 'en'}, {'file': b + '_raw.wav'}))
    if not os.path.exists(b + '_vo.mp3'):
        open(b + '_vo.mp3', 'wb').write(post(f'https://api.elevenlabs.io/v1/speech-to-speech/{V}?output_format=mp3_44100_192',
                                             {'model_id': 'eleven_multilingual_sts_v2', 'remove_background_noise': 'true', 'voice_settings': VS}, {'audio': b + '_raw.wav'}))
    d = json.load(open(b + '_stt.json', encoding='utf-8'))
    w = [x for x in d['words'] if x['type'] == 'word']
    said = d['text'].split('[')[0].strip()
    print(s['id'], round(w[0]['start'], 2), round(w[-1]['end'], 2), 'OK ' if norm(said) == norm(s['line']) else 'CHECK', '|', said)

if not os.path.exists(f'{OUT}/cta_vo.mp3'):
    open(f'{OUT}/cta_vo.mp3', 'wb').write(post(f'https://api.elevenlabs.io/v1/text-to-speech/{V}?output_format=mp3_44100_192',
                                               body={'text': P['cta']['line'], 'model_id': 'eleven_multilingual_v2', 'voice_settings': json.loads(VS)}))
    print('cta_vo OK')
