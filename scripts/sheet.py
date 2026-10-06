"""sheet.py clip.mp4 [fps=2] [out.jpg]

Tile frames of a clip into one contact sheet so motion can be reviewed from a still image:
check the face stays the same, the product print stays readable, and find trim points."""
import subprocess, sys

src = sys.argv[1]
fps = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
out = sys.argv[3] if len(sys.argv) > 3 else src.rsplit('.', 1)[0] + '_sheet.jpg'
d = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', src]))
n = int(d * fps) + 1
cols = 5
rows = -(-n // cols)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vf', f'fps={fps},scale=384:-2,tile={cols}x{rows}', '-frames:v', '1', out], check=True)
print(out, f'- {n} frames, one every {1 / fps:.2f}s, left to right then top to bottom')
