"""Archive thumbnails: one 600 px (long side) JPEG per photo in data/photos.json, then w/h written back.
Only makes thumbnails that are missing, so re-running after adding photos is cheap.

    ~/.cache/orbit-render/v/bin/python -I scripts/fa_thumbs.py      # Pillow lives in that Python
FA_DATA=<dir> reads/writes another data folder.
"""
import json
import os

from PIL import Image, ImageOps

MAT = 44  # 41 px mat + the JPEG's soft edge
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.environ.get('FA_DATA') or os.path.join(ROOT, 'data')
path = os.path.join(DATA, 'photos.json')
photos = json.load(open(path, encoding='utf-8'))

made = 0
for p in photos:
    out = os.path.join(ROOT, p['thumb'])
    if not os.path.exists(out):
        os.makedirs(os.path.dirname(out), exist_ok=True)
        im = ImageOps.exif_transpose(Image.open(os.path.join(ROOT, p['image']))).convert('RGB')
        if p['image'].startswith('assets/boulevard/'):  # the rooms print a 41 px cream mat into each file; the archive shows the photo only
            im = im.crop((MAT, MAT, im.width - MAT, im.height - MAT))
        im.thumbnail((600, 600), Image.LANCZOS)
        im.save(out, 'JPEG', quality=82, optimize=True, progressive=True)
        made += 1
    p['w'], p['h'] = Image.open(out).size

# same format as photosJson() in assets/archive/core.js: one record per line
with open(path, 'w', encoding='utf-8') as f:
    f.write('[\n' + ',\n'.join(json.dumps(p, ensure_ascii=False, separators=(',', ':')) for p in photos) + '\n]\n')
print(f'{made} thumbnails made, {len(photos)} sized')
