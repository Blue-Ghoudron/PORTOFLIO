"""Tagging page (F.A, pf-coe.6) on fake test photos: edit several photos at once, add a new artist,
save as downloads, and refuse to save broken data.

    python3 -m http.server 8031 --bind 127.0.0.1          # from the repo root
    ~/.venvs/playwright/bin/python -I tests/fa_tag.py [base-url]

Prints FAILS: none and exits 0 when everything works.
"""
import json
import os
import sys

from playwright.sync_api import sync_playwright

B = (sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8031/').rstrip('/') + '/'
T = B + 'tools/tag.html'
FX = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures', 'fa')

fails = []
def ok(cond, msg):
    if not cond:
        fails.append(msg)


def page(browser, photos=None):
    pg = browser.new_page(viewport={'width': 1440, 'height': 900}, accept_downloads=True)
    pg.errs, pg.files = [], {}
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.on('download', lambda d: pg.files.__setitem__(d.suggested_filename, open(d.path(), encoding='utf-8').read()))
    pg.add_init_script('delete window.showDirectoryPicker')  # force the download path

    def serve(route):
        name = route.request.url.split('?')[0].rsplit('/', 1)[1]
        body = photos if photos is not None and name == 'photos.json' else open(os.path.join(FX, name), encoding='utf-8').read()
        route.fulfill(status=200, content_type='application/json', body=body)
    pg.route('**/data/*.json', serve)
    pg.goto(T)
    pg.wait_for_selector('.sheet figure[data-id=test-12]')
    return pg


with sync_playwright() as p:
    browser = p.chromium.launch()

    pg = page(browser)
    ok(pg.get_attribute('meta[name=robots]', 'content') == 'noindex', 'noindex')
    ok(pg.locator('.sheet figure').count() == 12, 'contact sheet shows every photo')
    pg.check('#untagged')
    ok(pg.locator('.sheet figure:visible').count() == 1, 'only untagged: test-11')
    pg.uncheck('#untagged')

    pg.click('.sheet figure[data-id=test-11]')
    pg.click('.sheet figure[data-id=test-02]', modifiers=['Control'])
    ok(pg.locator('.sheet figure.sel').count() == 2, 'two photos selected')
    pg.check('#form input[name=genre][value=festival]')
    pg.once('dialog', lambda d: d.accept('Test Band C'))
    pg.click('#form button.new[data-list=artists]')
    pg.click('#save')
    pg.wait_for_timeout(800)
    ok(set(pg.files) == {'photos.json', 'refs.json'}, f'downloads: {list(pg.files)}')
    if 'photos.json' in pg.files:
        saved = pg.files['photos.json'].split('\n')
        orig = open(os.path.join(FX, 'photos.json'), encoding='utf-8').read().split('\n')
        ok(len(saved) == len(orig), 'same number of lines')
        for a, b in zip(saved, orig):
            if '"test-02"' in b or '"test-11"' in b:
                r = json.loads(a.rstrip(','))
                ok('festival' in r['genres'], f'{r["id"]} tagged festival')
                ok('test-band-c' in r['artistIds'], f'{r["id"]} gets the new artist')
            else:
                ok(a == b, f'untouched line changed: {b[:40]}')
    if 'refs.json' in pg.files:
        artists = json.loads(pg.files['refs.json'])['artists']
        ok({'id': 'test-band-c', 'label': 'Test Band C'} in artists, f'new artist saved: {artists}')
    ok(not pg.errs, f'errors: {pg.errs}')
    pg.close()

    # Review Focus 5: broken data is never written
    broken = open(os.path.join(FX, 'photos.json'), encoding='utf-8').read().replace('"locationId":"seamens-club"', '"locationId":"ghost"')
    pg = page(browser, photos=broken)
    pg.click('#save'); pg.wait_for_timeout(800)
    ok('unknown location "ghost"' in (pg.text_content('#errors') or ''), 'broken reference is reported')
    ok(not pg.files, f'nothing saved when data is broken: {list(pg.files)}')
    pg.close()

    # real data: loads all 159, and saving without edits gives back the same bytes (no noise in git diff)
    pg = browser.new_page(viewport={'width': 1440, 'height': 900}, accept_downloads=True)
    pg.files, pg.errs = {}, []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.on('download', lambda d: pg.files.__setitem__(d.suggested_filename, open(d.path(), encoding='utf-8').read()))
    pg.add_init_script('delete window.showDirectoryPicker')
    pg.goto(T); pg.wait_for_selector('.sheet figure')
    ok(pg.locator('.sheet figure').count() == 159, 'real data: 159 photos on the sheet')
    pg.click('#save'); pg.wait_for_timeout(800)
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for name in ['photos.json', 'refs.json']:
        ok(pg.files.get(name) == open(os.path.join(root, 'data', name), encoding='utf-8').read(), f'real data: {name} round-trips byte for byte')
    ok(not pg.errs, f'real data errors: {pg.errs}')
    pg.close()

    browser.close()

print('FAILS:', 'none' if not fails else '')
for f in fails:
    print(' -', f)
sys.exit(1 if fails else 0)
