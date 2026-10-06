"""gen_image.py OUT.png ASPECT "PROMPT" [ref1 ref2 ...]

Generate a keyframe with a Gemini image model, optionally guided by reference images
(product photo, an earlier keyframe of the same character, a style frame).
Also saves OUT.jpg (max 1920 px), which is what make_shots.py expects.
Set IMAGE_MODEL to use a different Gemini image model."""
import base64, mimetypes, os, sys
from common import key, post_json

MODEL = os.environ.get('IMAGE_MODEL', 'gemini-3-pro-image')


def gen(out, aspect, prompt, refs=()):
    parts = [{'inline_data': {'mime_type': mimetypes.guess_type(r)[0] or 'image/jpeg',
                              'data': base64.b64encode(open(r, 'rb').read()).decode()}} for r in refs]
    parts.append({'text': prompt})
    body = {'contents': [{'parts': parts}],
            'generationConfig': {'responseModalities': ['IMAGE'], 'imageConfig': {'aspectRatio': aspect, 'imageSize': '2K'}}}
    r, err = post_json(f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent',
                       body, {'x-goog-api-key': key('GEMINI_API_KEY')}, 300)
    if err:
        print('ERROR', out, err)
        return False
    for p in r.get('candidates', [{}])[0].get('content', {}).get('parts', []):
        d = p.get('inlineData') or p.get('inline_data')
        if d:
            open(out, 'wb').write(base64.b64decode(d['data']))
            try:
                from PIL import Image
                im = Image.open(out).convert('RGB')
                im.thumbnail((1920, 1920))
                im.save(os.path.splitext(out)[0] + '.jpg', quality=92)
            except Exception:
                pass
            print('OK', out)
            return True
    print('NO IMAGE', out)
    return False


if __name__ == '__main__':
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    sys.exit(0 if gen(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]) else 1)
