"""make_shots.py project.json

Animate each keyframe into a ~10 s clip with lip-synced speech (Gemini Omni Flash, Interactions API).
Clips that already exist are skipped: delete a clip to regenerate it."""
import base64, concurrent.futures as cf, os
from common import key, project, post_json

P = project()
OUT = P['dir'] + '/out'
MODEL = P.get('video_model', 'gemini-omni-1.1-flash')


def shot(s):
    out = f"{OUT}/{s['id']}.mp4"
    if os.path.exists(out):
        return out + ' (exists)'
    img = base64.b64encode(open(s['image'], 'rb').read()).decode()
    prompt = s.get('prompt') or (f"Animate this image into a video with synchronized audio. {s['action']} "
                                 f"in a {P['voice_direction']}: \"{s['line']}\" {P['style']}")
    body = {'model': MODEL, 'input': [{'type': 'image', 'data': img, 'mime_type': 'image/jpeg'}, {'type': 'text', 'text': prompt}]}
    r, err = post_json('https://generativelanguage.googleapis.com/v1beta/interactions', body, {'x-goog-api-key': key('GEMINI_API_KEY')})
    if err:
        return f'{out} {err}'
    for st in r.get('steps', []):
        for c in (st.get('content', []) if st.get('type') == 'model_output' else []):
            if c.get('type') == 'video':
                open(out, 'wb').write(base64.b64decode(c['data']))
                return out + ' OK'
    return out + ' NO VIDEO'


with cf.ThreadPoolExecutor(5) as ex:
    for res in ex.map(shot, P['shots']):
        print(res)
