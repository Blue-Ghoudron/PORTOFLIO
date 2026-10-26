"""Page editor (tools/pages.html): reorder, remove, featured, menu photo, add a file, save.
Saving goes to an in-memory folder (reads come from the server), so the site itself is never written.

    ~/.venvs/playwright/bin/python -I tests/pages_tool.py [base-url]   # default http://localhost:8026/
"""
import json
import os
import re
import sys

from playwright.sync_api import sync_playwright

B = (sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8026/').rstrip('/') + '/'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILS = []
ok = lambda c, m: c or FAILS.append(m)

# a folder handle whose files are the server's until written; writes and deletions are recorded
FAKE_DIR = """
window.__fs = {writes: {}, removed: []};
const read = p => fetch('/' + p, {cache: 'no-store'}).then(r => { if (!r.ok) throw new DOMException(p, 'NotFoundError'); return r.blob(); });
const dirAt = path => ({kind: 'directory',
  getDirectoryHandle: async n => dirAt(path + n + '/'),
  getFileHandle: async (n, o = {}) => { const p = path + n;
    if (!(p in __fs.writes) && !o.create) await read(p);
    return {kind: 'file', getFile: async () => new File([p in __fs.writes ? __fs.writes[p] : await read(p)], n),
      createWritable: async () => { let d; return {write: async x => { d = x; }, close: async () => { __fs.writes[p] = d; }}; }}; },
  removeEntry: async n => { __fs.removed.push(path + n); }});
window.showDirectoryPicker = async () => dirAt('');
"""

html = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
orig = json.loads('[' + re.search(r"\{id:'soualem'.*?imgs:\[(.*?)\]", html).group(1) + ']')

with sync_playwright() as p:
    pg = p.chromium.launch().new_page(viewport={'width': 1440, 'height': 900})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.add_init_script(FAKE_DIR)
    pg.route('**/__can-save', lambda r: r.fulfill(status=404))  # the fake folder, never scripts/serve.py writing the real site
    pg.goto(B + 'tools/pages.html'); pg.wait_for_selector('.tiles li')
    pg.select_option('#page', 'photography|soualem|'); pg.wait_for_timeout(200)
    tile = lambda i, a: pg.locator(f'.tiles li[data-i="{i}"] [data-a="{a}"]')
    ok(pg.locator('.tiles li').count() == len(orig), f'soualem shows {pg.locator(".tiles li").count()} of {len(orig)}')
    tile(0, 'right').click()                        # o1 o0 o2 o3 ...
    ok(pg.evaluate('document.activeElement.dataset.a') == 'right', 'focus follows the moved photo')
    tile(1, 'x').click()                            # o1 o2 o3 ...   (o0 removed)
    tile(0, 'star').click()                         # o1 featured
    tile(2, 'th').click()                           # o3 menu photo
    pg.set_input_files('#files', files=[{'name': 'IMG_7777.jpg', 'mimeType': 'image/jpeg',
                                         'buffer': open(os.path.join(ROOT, 'assets/home/soualem-9173.jpg'), 'rb').read()}])
    pg.wait_for_selector('.tiles li.new')
    ok('no camera line' in pg.locator('.tiles li.new').inner_text(), 'a web copy has no camera line')
    pg.click('#save'); pg.wait_for_function("document.getElementById('status').textContent === 'saved' || document.getElementById('errors').textContent")
    ok(pg.text_content('#errors') == '', 'save error: ' + pg.text_content('#errors'))

    fs = pg.evaluate("""async () => { const t = {}; for (const [k, v] of Object.entries(__fs.writes)) t[k] = typeof v === 'string' ? v : 'blob:' + v.size; return [t, __fs.removed]; }""")
    w, removed = fs
    want = [orig[1]] + orig[2:] + ['soualem-7777']
    line = re.search(r"^    \{id:'soualem'.*$", w.get('index.html', ''), re.M)
    ok(line and json.loads('[' + re.search(r'imgs:\[(.*?)\]', line.group(0)).group(1) + ']') == want, 'saved order')
    ok(line and f"th:'{orig[3]}'" in line.group(0), 'saved menu photo')
    ok(re.search(r'labels\.js\?v=[0-9a-f]{8}"', w.get('index.html', '')), 'labels.js cache-buster')
    ok(f'"{orig[0]}"' not in w.get('assets/home/labels.js', f'"{orig[0]}"'), 'removed photo loses its caption')
    recs = {r['id']: r for r in json.loads(w.get('data/photos.json', '[]'))}
    ok(orig[0] not in recs, 'removed photo leaves the archive')
    ok(recs.get(orig[1], {}).get('featured') is True, 'featured saved')
    ok(recs.get(orig[1], {}).get('alt') == 'Soualem, photo 1', 'alt renumbered')
    new = recs.get('soualem-7777', {})
    ok(new.get('w') and new.get('thumb') == 'assets/archive/t/soualem-7777.jpg', f'new archive record {new}')
    ok(str(w.get('assets/home/soualem-7777.jpg', '')).startswith('blob:') and 'assets/archive/t/soualem-7777.jpg' in w, 'new pictures written')
    ok(f'assets/home/{orig[0]}.jpg' in removed, f'removed photo file deleted: {removed}')
    ok(not errs, f'page errors: {errs}')

print('FAILS:', FAILS or 'none')
sys.exit(1 if FAILS else 0)
