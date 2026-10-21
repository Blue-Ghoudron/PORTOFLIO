"""Archive (F.A, pf-coe.4/5): the brief's acceptance criteria on fake test photos (tests/fixtures/fa/),
served in place of data/*.json with page.route, plus a pass over the real data.

    python3 -m http.server 8031 --bind 127.0.0.1          # from the repo root
    ~/.venvs/playwright/bin/python -I tests/fa_archive.py [base-url]   # default http://localhost:8031/

Prints FAILS: none and exits 0 when everything works.
"""
import os
import sys

from playwright.sync_api import sync_playwright

B = (sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8031/').rstrip('/') + '/'
A = B + 'index.html#photography/archive'
FX = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures', 'fa')

fails = []
def ok(cond, msg):
    if not cond:
        fails.append(msg)


def fixtures(pg):
    def serve(route):
        name = route.request.url.split('?')[0].rsplit('/', 1)[1]
        route.fulfill(status=200, content_type='application/json', body=open(os.path.join(FX, name), encoding='utf-8').read())
    pg.route('**/data/*.json', serve)


def open_page(browser, w, h, fake=True):
    pg = browser.new_page(viewport={'width': w, 'height': h})
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.on('response', lambda r: r.status >= 400 and pg.errs.append(f'{r.status} {r.url}'))
    if fake:
        fixtures(pg)
    return pg


def count(pg, n, msg):
    want = f'{n} photograph' + ('' if n == 1 else 's')
    try:
        pg.wait_for_function('t => document.querySelector(".fa-count")?.textContent === t', arg=want, timeout=3000)
    except Exception:
        ok(False, f'{msg}: want "{want}", got "{pg.text_content(".fa-count") if pg.query_selector(".fa-count") else None}"')


def tick(pg, field, value):
    dd = f'details.fa-dd[data-field={field}]'
    if not pg.eval_on_selector(dd, 'd => d.open'):
        pg.click(f'{dd} summary')
    pg.click(f'{dd} input[value="{value}"]')


def go(pg, url):
    pg.goto('about:blank')
    pg.goto(url)
    pg.wait_for_selector('.fa-count')


with sync_playwright() as p:
    browser = p.chromium.launch()

    # desktop, fake photos: acceptance criteria 1-8
    pg = open_page(browser, 1440, 900)
    go(pg, A)
    count(pg, 12, 'all photos')
    pg.click('[data-genre=music]'); count(pg, 8, 'music')
    pg.click('[data-genre=concert]'); count(pg, 5, 'AC1 concert from all places')
    tick(pg, 'location', 'american-arts-center'); count(pg, 4, 'AC2 place narrows')
    ok(pg.query_selector('.fa-chip[data-value=american-arts-center]'), 'AC2 place chip')
    ok(not pg.query_selector('[data-genre=american-arts-center]'), 'AC2 a place is never a genre')
    ok(not pg.query_selector('details.fa-dd[data-field=city]'), 'AC8 one-choice city hidden')
    ok(not pg.query_selector('.fa-dd .n:text-is("(0)")'), 'AC8 no zero options')
    tick(pg, 'year', '2026'); count(pg, 2, 'AC3 year narrows')
    ok(pg.url.endswith('#photography/archive?genre=concert&location=american-arts-center&year=2026'), f'AC7 address {pg.url}')
    pg.click('[data-genre=music]'); pg.click('[data-genre=festival]'); count(pg, 2, 'AC4 genre change')
    ok(not pg.query_selector('.fa-chip[data-value=american-arts-center]'), 'AC4 zero-match place dropped')
    ok(pg.query_selector('.fa-chip[data-value="2026"]'), 'AC4 matching year kept')
    pg.click('.fa-clear'); count(pg, 12, 'AC5 clear all')
    ok(pg.url.endswith('#photography/archive'), f'AC5 address {pg.url}')
    pg.click('[data-genre=music]'); pg.click('[data-genre=festival]')
    ok(pg.query_selector('figure[data-id=test-05]'), 'AC6 series photo in genre results')
    pg.click('figure[data-id=test-05]')
    ok(pg.locator('#lb.on').is_visible(), 'viewer opens')
    ok((pg.get_attribute('#lb-from', 'href') or '').endswith('#photography/boulevard/Band'), 'AC6 viewer links to its series')
    ok('TEST SERIES' in (pg.text_content('#lb-from') or ''), 'AC6 viewer names its series')
    pg.keyboard.press('Escape')

    go(pg, A + '?genre=concert&location=american-arts-center&year=2026'); count(pg, 2, 'AC7 address restores the view')
    ok(len(pg.query_selector_all('.fa-chip')) == 3, 'AC7 restored chips (genre, place, year)')
    go(pg, A + '?genre=nope&year=abc&location=ghost&foo=1'); count(pg, 12, 'AC7 invalid params ignored')
    go(pg, A + '?genre=festival&location=seamens-club'); count(pg, 0, 'AC8 empty result')
    ok(pg.locator('.fa-empty').is_visible(), 'AC8 empty state shown')
    pg.click('.fa-reset'); count(pg, 12, 'AC8 reset')
    ok(not pg.errs, f'desktop errors: {pg.errs}')
    pg.close()

    # desktop, real photos
    pg = open_page(browser, 1440, 900, fake=False)
    go(pg, A)
    count(pg, 159, 'real archive')
    ok('159' in pg.text_content('a.arch'), 'menu row shows the total')
    ok(pg.get_attribute('a.arch', 'aria-current') == 'page', 'menu row is current')
    ok(not pg.query_selector('.fa-genres'), 'no genre row before tagging')
    pg.click('.fa-grid figure >> nth=0')
    src = pg.get_attribute('#lb-i', 'src') or ''
    ok('assets/archive/t/' not in src and src.endswith('.jpg'), f'viewer shows the full image, not the thumbnail: {src}')
    pg.keyboard.press('Escape')
    ok(not pg.errs, f'real data errors: {pg.errs}')
    pg.close()

    browser.close()

print('FAILS:', 'none' if not fails else '')
for f in fails:
    print(' -', f)
sys.exit(1 if fails else 0)
