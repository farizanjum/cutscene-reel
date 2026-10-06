"""build.py project.json

Assemble the final video: trim each shot to its speech, crop and upscale, burn captions from the
word timestamps, add the end card(s), mix the voice over the music. Writes final/<name>.mp4 and,
if the project has a "tag", final/<name>_<suffix>.mp4."""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from common import project

P = project()
W, H = P.get('size', [1440, 1080])  # 4:3 like the reference format; use [1920, 1080] to keep 16:9
FPS = 24
CRF_I, CRF_F, ABR = str(P.get('crf_intermediate', 14)), str(P.get('crf_final', 16)), P.get('audio_bitrate', '256k')
OUT, BUILD = P['dir'] + '/out', P['dir'] + '/build'
os.makedirs(BUILD, exist_ok=True)
os.makedirs('final', exist_ok=True)
ENC = ['-r', str(FPS), '-c:v', 'libx264', '-crf', CRF_I, '-preset', 'slow', '-pix_fmt', 'yuv420p', '-c:a', 'pcm_s16le', '-ar', '48000', '-ac', '2']
VF = f'crop=ih*{W}/{H}:ih,scale={W}:{H}:flags=lanczos,unsharp=5:5:0.6,fps={FPS}'


def font(size):
    for f in [P.get('font'), 'C:/Windows/Fonts/arialbd.ttf', '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
              '/Library/Fonts/Arial Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
              '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf']:
        if f and os.path.exists(f):
            return ImageFont.truetype(f, size)
    sys.exit('No bold sans font found. Set "font" in project.json to a .ttf path.')


FONT = font(round(H * 0.057))
LINE = round(H * 0.065)


def run(*a):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *a], check=True)


def caption_png(text, path):
    """White bold lowercase caption with a soft black shadow, centred in the lower third."""
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(im), ImageDraw.Draw(sh)
    lines, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=FONT) > W * 0.78 and cur:
            lines.append(cur)
            cur = w
        else:
            cur = t
    lines.append(cur)
    y = H - round(H * 0.14) - LINE * len(lines)
    for ln in lines:
        x = (W - d.textlength(ln, font=FONT)) / 2
        for _ in range(3):
            ds.text((x, y + 3), ln, font=FONT, fill=(0, 0, 0, 255), stroke_width=5, stroke_fill=(0, 0, 0, 255))
        d.text((x, y), ln, font=FONT, fill=(255, 255, 255, 255))
        y += LINE
    Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)), im).save(path)


def chunks(words, max_words=6, max_chars=30):
    """Group words into caption cards of 2-7 words, breaking on punctuation."""
    out, cur = [], []
    for w in words:
        cur.append(w)
        txt = ' '.join(x['text'] for x in cur)
        if w['text'][-1] in '.?!' or (w['text'][-1] == ',' and len(cur) >= 3) or len(cur) >= max_words or len(txt) >= max_chars:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    i = 1
    while i < len(out):  # no one-word orphans unless they are a full sentence on their own
        if len(out[i]) == 1 and out[i - 1][-1]['text'][-1] not in '.?!':
            out[i - 1] += out.pop(i)
        else:
            i += 1
    return out


def make_silent(s):
    """A hook or action shot with no speech: trim, optionally speed up, keep its own sound effects."""
    t0, t1 = s['trim']
    sp = s.get('speed', 1.0)
    dur = (t1 - t0) / sp
    af = (f'atempo={sp:.3f},' if sp != 1 else '') + f"volume={s.get('sfx_gain', 0.5)},apad"
    dst = f"{BUILD}/{s['id']}.mov"
    run('-ss', f'{t0:.3f}', '-t', f'{t1 - t0:.3f}', '-i', f"{OUT}/{s['id']}.mp4", '-vf', f'setpts=PTS/{sp},{VF}', '-af', af, '-t', f'{dur:.3f}', *ENC, dst)
    return dst


def make_shot(s):
    if s.get('silent'):
        return make_silent(s)
    sid = s['id']
    words = [w for w in json.load(open(f'{OUT}/{sid}_stt.json', encoding='utf-8'))['words'] if w['type'] == 'word']
    t0 = max(0, words[0]['start'] - 0.12)
    dur = words[-1]['end'] + s.get('tail', 0.35) - t0
    ins = ['-ss', f'{t0:.3f}', '-t', f'{dur:.3f}', '-i', f'{OUT}/{sid}.mp4']
    flt, last = f'[0:v]{VF}[v0]', 'v0'
    ch = chunks(words)
    for i, c in enumerate(ch):
        png = f'{BUILD}/{sid}_c{i}.png'
        caption_png(' '.join(w['text'] for w in c).lower().rstrip('.,'), png)
        a = max(0, c[0]['start'] - t0 - 0.05)
        b = (ch[i + 1][0]['start'] - t0 - 0.05) if i + 1 < len(ch) else dur
        ins += ['-i', png]
        flt += f";[{last}][{i + 1}:v]overlay=enable='between(t,{a:.3f},{b:.3f})'[c{i}]"
        last = f'c{i}'
    dst = f'{BUILD}/{sid}.mov'
    run(*ins, '-ss', f'{t0:.3f}', '-t', f'{dur:.3f}', '-i', f'{OUT}/{sid}_vo.mp3', '-filter_complex', flt,
        '-map', f'[{last}]', '-map', f'{len(ch) + 1}:a', '-af', 'highpass=f=80,apad', '-t', f'{dur:.3f}', *ENC, dst)
    return dst


def make_card(name, image, caption, vo=None, dur=3.6, crop=None, bg=(11, 16, 48)):
    """A still end card: product photo or logo card, optional caption, optional voice line."""
    if image:
        im = Image.open(image).convert('RGB')
        if crop:
            im = im.crop(tuple(crop))
        im = im.resize((W, H), Image.LANCZOS)
    else:
        im = Image.new('RGB', (W, H), tuple(bg))
    im.save(f'{BUILD}/{name}_bg.png')
    caption_png(caption or '', f'{BUILD}/{name}_cap.png')
    a = ['-i', vo] if vo else ['-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo']
    dst = f'{BUILD}/{name}.mov'
    run('-loop', '1', '-t', str(dur), '-i', f'{BUILD}/{name}_bg.png', '-loop', '1', '-t', str(dur), '-i', f'{BUILD}/{name}_cap.png', *a,
        '-filter_complex', f'[0:v][1:v]overlay,fps={FPS}[v];[2:a]adelay=250:all=1,apad[a]', '-map', '[v]', '-map', '[a]', '-t', str(dur), *ENC, dst)
    return dst


def assemble(parts, out):
    open(f'{BUILD}/list.txt', 'w').write(''.join(f"file '{os.path.basename(p)}'\n" for p in parts))
    run('-f', 'concat', '-safe', '0', '-i', f'{BUILD}/list.txt', '-c', 'copy', f'{BUILD}/_cut.mov')
    d = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f'{BUILD}/_cut.mov']))
    vo = '[0:a]acompressor=threshold=-18dB:ratio=3:attack=5:release=80,volume=1.6[vo]'
    final = ['-c:v', 'libx264', '-crf', CRF_F, '-preset', 'slow', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-c:a', 'aac', '-b:a', ABR, '-t', f'{d:.2f}', out]
    if P.get('music'):
        run('-i', f'{BUILD}/_cut.mov', '-stream_loop', '-1', '-i', P['music'], '-filter_complex',
            f"{vo};[1:a]atrim=0:{d:.2f},asetpts=PTS-STARTPTS,volume={P.get('music_gain', 0.2)},afade=t=out:st={d - 0.8:.2f}:d=0.8[m];"
            f"[vo][m]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9[a]", '-map', '0:v', '-map', '[a]', *final)
    else:
        run('-i', f'{BUILD}/_cut.mov', '-filter_complex', f'{vo};[vo]loudnorm=I=-14:TP=-1.5:LRA=9[a]', '-map', '0:v', '-map', '[a]', *final)
    print(out, round(d, 2), 's')


shots = {s['id']: make_shot(s) for s in P['shots'] if not s.get('silent') or s.get('trim')}
cut = [shots[i] for i in P.get('cut_main', [s['id'] for s in P['shots'] if s['id'] in shots])]
if P.get('cta'):
    c = P['cta']
    vo = f'{OUT}/cta_vo.mp3'
    cut.append(make_card('cta', c.get('image'), c.get('caption'), vo if os.path.exists(vo) else None, c.get('duration', 3.6), c.get('crop')))
assemble(cut, f"final/{P['name']}.mp4")
if P.get('tag'):  # optional sting after the end card: one more shot, then a logo card
    t = P['tag']
    extra = ([shots[t['shot']]] if t.get('shot') else []) + [make_card('tag', t.get('image'), t.get('caption'), None, t.get('duration', 2.4), None, t.get('bg', (11, 16, 48)))]
    assemble(cut + extra, f"final/{P['name']}_{t.get('suffix', 'tag')}.mp4")
