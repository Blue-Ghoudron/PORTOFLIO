"""Add or refresh a homepage photo page from a Lightroom export folder, in one run.

    ~/.cache/orbit-render/v/bin/python -I scripts/add_page.py <export-folder> <id> [--name N] [--group G]
        [--section photography] [--info TEXT] [--city NAME] [--th ID] [--originals DIR]

The page shows exactly what is in the folder: Picks/ first, then loose files, then each subfolder (A-Z);
byte-identical files once. Each export is matched back to its camera JPG under --originals (default: the
folder's parent; numbers repeat across days, so the closest-looking one wins) for its camera line and date.
Writes assets/home/<prefix>-<n>.jpg (1600 px), the menu thumb, the WORK entry, labels.js (+ cache-buster),
and the archive records (dates, city; tags left alone), then runs fa_thumbs.py. Photos taken out of the
folder are taken off the page and out of the archive. Re-running with nothing changed changes nothing.
Contact sheet with flags (no original, near-duplicates): tests/out/<id>-sheet.jpg
"""
import argparse, hashlib, json, os, re, subprocess, sys
from PIL import Image, ImageChops, ImageDraw, ImageOps, ImageStat

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME, ARCH = os.path.join(ROOT, 'assets/home'), os.path.join(ROOT, 'assets/archive/t')
CAMERA = re.compile(r'([A-Za-z]+_?\d+)\.jpe?g', re.I)  # straight-from-camera names only, not "-edit-..." exports


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def q(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"


def date_range(dates):
    """['2026-03-21', '2026-03-26'] -> '21–26.03.2026'"""
    a, b = (d.split('-')[::-1] for d in (min(dates), max(dates)))
    if a == b: return '.'.join(a)
    if a[1:] == b[1:]: return f'{a[0]}–{".".join(b)}'
    if a[2] == b[2]: return f'{a[0]}.{a[1]}–{".".join(b)}'
    return f'{".".join(a)}–{".".join(b)}'


def exports(folder):
    subs = sorted((d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))), key=str.lower)
    seen, out = set(), []
    for d in [s for s in subs if s.lower() == 'picks'] + [''] + [s for s in subs if s.lower() != 'picks']:
        p = os.path.join(folder, d)
        for f in sorted(os.listdir(p)):
            if f.lower().endswith(('.jpg', '.jpeg')) and os.path.isfile(os.path.join(p, f)):
                h = hashlib.md5(open(os.path.join(p, f), 'rb').read()).hexdigest()
                if h not in seen: seen.add(h); out.append(os.path.join(d, f))
    return out


def gray(path, size=256):
    im = Image.open(path); im.draft('L', (size, size))
    return ImageOps.exif_transpose(im).convert('L')


def likeness(exp, cand):
    """Mean difference between the export and the best crop of the candidate (exports are often crops)."""
    e, c = gray(exp), gray(cand)
    e = ImageOps.equalize(e.resize((48, round(48 * e.height / e.width))))
    best = 1e9
    for z in (1, .9, .8, .7, .6, .5, .4, .3):
        w = c.width * z; h = w * e.height / e.width
        if h > c.height: continue
        for fx in (.5, .3, .7, 0, 1):
            for fy in (.5, .3, .7, 0, 1):
                x, y = (c.width - w) * fx, (c.height - h) * fy
                cc = ImageOps.equalize(c.crop((round(x), round(y), round(x + w), round(y + h))).resize(e.size))
                best = min(best, ImageStat.Stat(ImageChops.difference(cc, e)).mean[0])
    return best


def exif(path):
    ex = Image.open(path).getexif(); s = ex.get_ifd(0x8769)
    t, sh, fn, iso = s.get(36867), s.get(33434), s.get(33437), s.get(34855)
    if not (t and sh and fn and iso): return None
    sh = f'1/{round(1 / sh)} s' if sh < 1 else f'{float(sh):g} s'
    name = CAMERA.match(os.path.basename(path)) or re.match(r'([A-Za-z]+_?\d+)', os.path.basename(path))
    return t[:10].replace(':', '-'), f'{name.group(1)} · {t[11:]} · {sh} · f/{float(fn):g} · ISO {iso}'


def dhash(path):
    g = gray(path, 64).resize((9, 8)); px = g.tobytes()
    return sum(1 << i for i in range(64) if px[i // 8 * 9 + i % 8] > px[i // 8 * 9 + i % 8 + 1])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('folder'); ap.add_argument('id')
    for o in ('name', 'group', 'info', 'city', 'th', 'originals'): ap.add_argument('--' + o)
    ap.add_argument('--section', default='photography')
    a = ap.parse_args()
    folder = a.folder.rstrip('/'); originals = a.originals or os.path.dirname(folder)

    index = {}
    for r, _, fs in os.walk(originals):
        if os.path.abspath(r).startswith(os.path.abspath(folder)): continue
        for f in fs:
            m = CAMERA.fullmatch(f)
            if m: index.setdefault(m.group(1).upper(), []).append(os.path.join(r, f))

    photos, report = [], []
    for e in exports(folder):
        src = os.path.join(folder, e); stem = os.path.splitext(os.path.basename(e))[0]
        pid = f'{a.id}-' + slug(re.sub(r'^[A-Za-z]+_', '', stem))
        meta = exif(src)  # a straight camera JPG carries its own
        if not meta:
            key = re.match(r'([A-Za-z]+_?\d+)', stem); cands = index.get(key.group(1).upper(), []) if key else []
            scored = sorted((likeness(src, c), c) for c in cands)
            if scored:
                meta = exif(scored[0][1])
                if len(scored) > 1 and scored[1][0] - scored[0][0] < 10:
                    report.append(f'{pid}: original unsure, took {os.path.relpath(scored[0][1], originals)}')
        if not meta: report.append(f'{pid}: no camera original, no camera line')
        photos.append({'id': pid, 'src': src, 'export': e, 'date': meta and meta[0], 'label': meta and meta[1]})

    # web copies (remade when the export is newer)
    made = 0
    for p in photos:
        out = os.path.join(HOME, p['id'] + '.jpg')
        if not os.path.exists(out) or os.path.getmtime(p['src']) > os.path.getmtime(out):
            im = ImageOps.exif_transpose(Image.open(p['src'])).convert('RGB'); im.thumbnail((1600, 1600), Image.LANCZOS)
            im.save(out, 'JPEG', quality=82, optimize=True, progressive=True); made += 1
            if os.path.exists(os.path.join(ARCH, p['id'] + '.jpg')): os.remove(os.path.join(ARCH, p['id'] + '.jpg'))
    ids = [p['id'] for p in photos]

    # WORK entry: replace the project's line, or add it after its group (else at the end of the section)
    html = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    line = re.search(rf"^    \{{id:'{re.escape(a.id)}',.*$\n", html, re.M)
    old = {}
    if line:
        for k in ('group', 'name', 'th', 'info'):
            m = re.search(rf"\b{k}:'((?:[^'\\]|\\.)*)'", line.group(0))
            if m: old[k] = m.group(1).replace("\\'", "'")
        old_ids = re.findall(r'"([^"]+)"|\'([^\']+)\'', line.group(0).split('imgs:')[1])
        old_ids = [x or y for x, y in old_ids]
    else:
        old_ids = []
    name = a.name or old.get('name') or a.id.capitalize()
    group = a.group or old.get('group')
    th = a.th or (old.get('th') if old.get('th') in ids else None) or ids[0]
    dates = [p['date'] for p in photos if p['date']]
    info = a.info or old.get('info') or (date_range(dates) if dates else '')
    entry = '    {' + ', '.join([f'id:{q(a.id)}'] + ([f'group:{q(group)}'] if group else []) + [f'name:{q(name)}', f'th:{q(th)}', f'info:{q(info)}']) + ', imgs:' + json.dumps(ids, ensure_ascii=False).replace('","', '", "') + '},\n'
    if line:
        html = html.replace(line.group(0), entry)
    else:
        sec = html.index(f"{{id:'{a.section}'"); end = html.index('\n  ]},', sec) + 1
        grp = [m for m in re.finditer(rf"^    \{{id:'[^']+', group:{re.escape(q(group or ''))}.*$\n", html[sec:end], re.M)] if group else []
        at = sec + grp[-1].end() if grp else end
        html = html[:at] + entry + html[at:]
    gone = [i for i in old_ids if i not in ids]

    # labels.js: set this page's lines, drop removed ones; version the script tag so browsers reload it
    lp = os.path.join(HOME, 'labels.js'); src = open(lp, encoding='utf-8').read()
    head = src[:src.index('const LABELS = {')]
    labels = dict(re.findall(r'^"([^"]+)": "([^"]*)"', src, re.M))
    for i in gone: labels.pop(i, None)
    for p in photos:
        if p['label']: labels[p['id']] = p['label']
        else: labels.pop(p['id'], None)
    body = head + 'const LABELS = {\n' + ',\n'.join(f'"{k}": "{v}"' for k, v in sorted(labels.items())) + '\n};\n'
    open(lp, 'w', encoding='utf-8').write(body)
    html = re.sub(r'assets/home/labels\.js(\?v=\w+)?"', f'assets/home/labels.js?v={hashlib.md5(body.encode()).hexdigest()[:8]}"', html)
    open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(html)

    # menu thumb
    tt = os.path.join(HOME, 't', th + '.jpg')
    if not os.path.exists(tt) or os.path.getmtime(os.path.join(HOME, th + '.jpg')) > os.path.getmtime(tt):
        im = Image.open(os.path.join(HOME, th + '.jpg')).convert('RGB'); im.thumbnail((192, 120), Image.LANCZOS)  # whole picture: the menu never crops
        im.save(tt, quality=82, optimize=True)

    # archive: one record per photo; tags people set are kept, dates/alt/city filled from the files
    dp = os.path.join(ROOT, 'data'); recs = json.load(open(os.path.join(dp, 'photos.json'), encoding='utf-8'))
    refs = json.load(open(os.path.join(dp, 'refs.json'), encoding='utf-8'))
    city = None
    if a.city:
        city = slug(a.city)
        if not any(c['id'] == city for c in refs['cities']):
            refs['cities'].append({'id': city, 'label': a.city})
            open(os.path.join(dp, 'refs.json'), 'w', encoding='utf-8').write(json.dumps(refs, ensure_ascii=False, indent=1) + '\n')
    by = {r['id']: r for r in recs}
    recs = [r for r in recs if r['id'] not in gone]
    for n, p in enumerate(photos, 1):
        r = by.get(p['id'])
        if not r:
            r = {'id': p['id'], 'title': None, 'image': f"assets/home/{p['id']}.jpg", 'thumb': f"assets/archive/t/{p['id']}.jpg", 'w': None, 'h': None,
                 'discipline': 'photography', 'genres': [], 'locationId': None, 'cityId': None, 'year': None, 'date': None,
                 'eventIds': [], 'artistIds': [], 'clientId': None, 'featured': False, 'alt': ''}
            recs.append(r)
        r['alt'] = f'{name}, photo {n}'
        if p['date'] and not r['date']: r['date'], r['year'] = p['date'], int(p['date'][:4])
        if city and not r['cityId']: r['cityId'] = city
    with open(os.path.join(dp, 'photos.json'), 'w', encoding='utf-8') as f:
        f.write('[\n' + ',\n'.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) for r in recs) + '\n]\n')
    for i in gone:
        for f in (os.path.join(ARCH, i + '.jpg'), os.path.join(HOME, i + '.jpg'), os.path.join(HOME, 't', i + '.jpg')):
            if os.path.exists(f) and not re.search(rf"['\"]{re.escape(i)}['\"]", html): os.remove(f)
    subprocess.run([sys.executable, '-I', os.path.join(ROOT, 'scripts/fa_thumbs.py')], check=True)

    # contact sheet + near-duplicate flags
    hashes = [(p['id'], dhash(p['src'])) for p in photos]
    for k, (i, h) in enumerate(hashes):
        for j, g in hashes[k + 1:]:
            if bin(h ^ g).count('1') <= 10: report.append(f'{i} ~ {j}: look alike')
    W, H, cols = 260, 290, 6
    sheet = Image.new('RGB', (W * cols, H * -(-len(photos) // cols)), 'white'); d = ImageDraw.Draw(sheet)
    for k, p in enumerate(photos):
        im = ImageOps.exif_transpose(Image.open(os.path.join(HOME, p['id'] + '.jpg'))).convert('RGB'); im.thumbnail((250, 250))
        x, y = k % cols * W, k // cols * H
        sheet.paste(im, (x + 5, y + 5)); d.text((x + 5, y + 262), f"{k + 1:02} {p['id']}  {p['export']}"[:44], fill='black' if p['label'] else 'red')
    os.makedirs(os.path.join(ROOT, 'tests/out'), exist_ok=True)
    sheet.save(os.path.join(ROOT, 'tests/out', a.id + '-sheet.jpg'), quality=80)

    print(f"{a.id}: {len(ids)} photos ({made} web copies made, {len(gone)} removed), group {group!r}, info {info!r}, thumb {th}")
    print('\n'.join(report) or 'no flags')
    print(f'sheet: tests/out/{a.id}-sheet.jpg')


if __name__ == '__main__':
    main()
