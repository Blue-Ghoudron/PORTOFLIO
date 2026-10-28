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
    was = tile(0, 'star').get_attribute('aria-pressed') == 'true'  # your selection may already hold o1
    tile(0, 'star').click()                         # o1 in or out of Selected work
    tile(2, 'th').click()                           # o3 menu photo
    pg.once('dialog', lambda d: d.accept("Soualem's Fields")); pg.click('#rename')
    ok("Soualem's Fields" in pg.locator('#page option:checked').inner_text(), 'rename shows in the page list')
    pg.set_input_files('#files', files=[{'name': 'IMG_7777.jpg', 'mimeType': 'image/jpeg',
                                         'buffer': open(os.path.join(ROOT, 'assets/home/soualem-9173.jpg'), 'rb').read()}])
    pg.wait_for_selector('.tiles li.new')
    ok('no camera line' in pg.locator('.tiles li.new').inner_text(), 'a web copy has no camera line')
    ok((tile(0, 'star').get_attribute('aria-pressed') == 'true') != was, 'the star flips')
    # Selected work: starts from what the site shows, gets the starred photo at the end; reorder, take one out
    pg.select_option('#page', 'selected|photography'); pg.wait_for_timeout(200)
    sel = pg.eval_on_selector_all('.tiles li', 'ls => ls.map(l => l.dataset.id)')
    ok((orig[1] in sel) != was and (was or sel[-1] == orig[1]), f'starring adds at the end, unstarring takes out: {sel[-3:]}')
    ok(pg.locator('.add:not([hidden])').count() == 0 and pg.locator('[data-a=th], [data-a=star]').count() == 0, 'no menu photo, star or add on Selected work')
    tile(0, 'right').click(); tile(1, 'x').click()
    want_sel = [sel[1]] + sel[2:]
    # Design: every poster until chosen; take the first one out
    pg.select_option('#page', 'selected|design'); pg.wait_for_timeout(200)
    des = pg.eval_on_selector_all('.tiles li', 'ls => ls.map(l => l.dataset.id)')
    saved_des = json.loads(re.search(r'^const SELECTED = (\{.*\});$', html, re.M).group(1)).get('design') or []
    ok(len(des) == (len(saved_des) or 39), f'design selection starts as the site shows it (its list, else every poster): {len(des)}')
    tile(0, 'x').click()
    # page order: the second group moves above the first, its first two pages swap; the new page below joins Places, last
    sec = re.search(r"^  \{id:'photography'.*?^  \]\},", html, re.M | re.S).group(0)
    projs = re.findall(r"^    \{id:'([^']+)'(?:, group:'([^']+)')?", sec, re.M)
    groups = list(dict.fromkeys(g for _, g in projs)); grp = lambda g: [i for i, gg in projs if gg == g]
    pg.select_option('#page', 'order|photography'); pg.wait_for_timeout(200)
    heads = lambda: pg.eval_on_selector_all('.tiles li.ghead b', 'bs => bs.map(b => b.textContent)')
    ok(heads() == groups, f'groups in menu order: {heads()} vs {groups}')
    pg.click('.tiles li[data-i="g1"] [data-a="up"]')
    ok(pg.evaluate('document.activeElement.dataset.a') == 'up' and heads()[:2] == [groups[1], groups[0]], 'a group moves up, focus follows')
    pg.click('.tiles li[data-i="0.0"] [data-a="right"]')
    ok(pg.locator('.add:not([hidden])').count() == 0, 'no add on page order')
    order = [groups[1], groups[0]] + groups[2:]
    ids_of = {g: grp(g) + (['test-page'] if g == 'Places' else []) for g in order}
    first = ids_of[groups[1]]; first[0], first[1] = first[1], first[0]
    want_order = [i for g in order for i in ids_of[g]]
    # a new page in Places, with one photo
    pg.click('#new'); pg.select_option('#nsec', 'photography'); pg.fill('#nname', 'Test Page'); pg.fill('#ngroup', 'Places')
    pg.fill('#ninfo', 'Somewhere · 01.01.2026'); pg.click('#newdlg .go')
    ok(pg.input_value('#page') == 'photography|test-page|' and pg.locator('.tiles li').count() == 0, 'the new page opens, empty')
    pg.set_input_files('#files', files=[{'name': 'IMG_8888.jpg', 'mimeType': 'image/jpeg',
                                         'buffer': open(os.path.join(ROOT, 'assets/home/soualem-9173.jpg'), 'rb').read()}])
    pg.wait_for_selector('.tiles li.new')
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
    ok(recs.get(orig[1], {}).get('featured') is (orig[1] in want_sel), 'featured follows the photography selection')
    ok(recs.get(orig[1], {}).get('alt') == "Soualem's Fields, photo 1", 'alt renumbered, with the new name')
    ok(line and "name:'Soualem\\'s Fields'" in line.group(0), f'saved name: {line and line.group(0)[:90]}')
    new = recs.get('soualem-7777', {})
    ok(new.get('w') and new.get('thumb') == 'assets/archive/t/soualem-7777.jpg', f'new archive record {new}')
    ok(str(w.get('assets/home/soualem-7777.jpg', '')).startswith('blob:') and 'assets/archive/t/soualem-7777.jpg' in w, 'new pictures written')
    ok(f'assets/home/{orig[0]}.jpg' in removed, f'removed photo file deleted: {removed}')
    m = re.search(r'^const SELECTED = (\{.*\});$', w.get('index.html', ''), re.M)
    saved_sel = json.loads(m.group(1)) if m else {}
    ok(saved_sel.get('photography') == want_sel, f'photography selection saved: {str(saved_sel)[:120]}')
    ok(saved_sel.get('design') == des[1:] and saved_sel.get('workshops') == [], 'design selection saved, workshops left alone')
    ok(all(recs[i]['featured'] for i in want_sel if i in recs) and not recs.get(sel[0], {}).get('featured'), 'featured flags follow the selection')
    ok(f'assets/home/{sel[0]}.jpg' not in removed, 'taking a photo out of the selection deletes nothing')
    page_line = re.search(r"^    \{id:'test-page'.*$", w.get('index.html', ''), re.M)
    ok(page_line and page_line.group(0) == "    {id:'test-page', group:'Places', name:'Test Page', info:'Somewhere · 01.01.2026', imgs:[\"test-page-8888\"]},", f'new page line: {page_line and page_line.group(0)}')
    lines = w.get('index.html', '').split('\n')
    ok(page_line and lines[lines.index(page_line.group(0)) - 1].startswith(f"    {{id:'{ids_of['Places'][-2]}'"), 'new page sits after the last Places page')
    ok(recs.get('test-page-8888', {}).get('alt') == 'Test Page, photo 1', 'new page photo in the archive')
    ok('assets/home/t/test-page-8888.jpg' in w and 'assets/home/test-page-8888.jpg' in w, 'new page photo and menu thumb written')
    saved_sec = re.search(r"^  \{id:'photography'.*?^  \]\},", w.get('index.html', ''), re.M | re.S)
    got = re.findall(r"^    \{id:'([^']+)'", saved_sec.group(0), re.M) if saved_sec else []
    ok(got == want_order, f'page order saved: {got}')
    ok(re.search(r"^  \{id:'design'.*?^  \]\},", w.get('index.html', ''), re.M | re.S).group(0) == re.search(r"^  \{id:'design'.*?^  \]\},", html, re.M | re.S).group(0), 'design order untouched')
    ok(not errs, f'page errors: {errs}')

    # an empty new page is not saved, and nothing is written
    pg2 = pg.context.browser.new_page(); pg2.add_init_script(FAKE_DIR); pg2.route('**/__can-save', lambda r: r.fulfill(status=404))
    pg2.goto(B + 'tools/pages.html'); pg2.wait_for_selector('.tiles li')
    pg2.click('#new'); pg2.select_option('#nsec', 'workshops'); pg2.fill('#nname', 'Empty'); pg2.click('#newdlg .go'); pg2.click('#save')
    pg2.wait_for_function("document.getElementById('errors').textContent")
    ok('no photos' in pg2.text_content('#errors') and pg2.evaluate('Object.keys(__fs.writes).length') == 0, 'empty new page refused, nothing written')

    # a menu photo from a file: only its small menu copy is written; the page, its captions and the archive stay as they were
    pg3 = pg.context.browser.new_page(); pg3.add_init_script(FAKE_DIR); pg3.route('**/__can-save', lambda r: r.fulfill(status=404))
    pg3.goto(B + 'tools/pages.html'); pg3.wait_for_selector('.tiles li'); pg3.select_option('#page', 'photography|jazz|'); pg3.wait_for_timeout(200)
    jazz = json.loads('[' + re.search(r"\{id:'jazz'.*?imgs:\[(.*?)\]", html).group(1) + ']')
    pg3.set_input_files('#thfile', files=[{'name': 'IMG_5555.jpg', 'mimeType': 'image/jpeg',
                                           'buffer': open(os.path.join(ROOT, 'assets/home/soualem-9173.jpg'), 'rb').read()}])
    pg3.wait_for_selector('#thnow:not([hidden])')
    ok(pg3.locator('.tiles li').count() == len(jazz) and pg3.locator('.tiles [data-a=th][aria-pressed=true]').count() == 0, 'menu-only photo is not a tile')
    pg3.click('#save'); pg3.wait_for_function("document.getElementById('status').textContent === 'saved' || document.getElementById('errors').textContent")
    ok(pg3.text_content('#errors') == '', 'menu-only save error: ' + pg3.text_content('#errors'))
    w3 = pg3.evaluate("Object.fromEntries(Object.entries(__fs.writes).map(([k, v]) => [k, typeof v === 'string' ? v : 'blob:' + v.size]))")
    jl = re.search(r"^    \{id:'jazz'.*$", w3.get('index.html', ''), re.M)
    ok(jl and "th:'jazz-5555'" in jl.group(0) and json.loads('[' + re.search(r'imgs:\[(.*?)\]', jl.group(0)).group(1) + ']') == jazz, f'menu-only th saved, photos unchanged: {jl and jl.group(0)[:90]}')
    ok('assets/home/t/jazz-5555.jpg' in w3 and 'assets/home/jazz-5555.jpg' not in w3 and 'assets/archive/t/jazz-5555.jpg' not in w3, f'only the menu copy written: {sorted(w3)}')
    ok('jazz-5555' not in w3.get('data/photos.json', '') and 'jazz-5555' not in w3.get('assets/home/labels.js', ''), 'no archive record or caption')

print('FAILS:', FAILS or 'none')
sys.exit(1 if FAILS else 0)
