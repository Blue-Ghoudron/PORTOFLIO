"""Click-through test: every menu link, the CTA, About, logo, theme switch, photo viewer,
every room inside the L'Boulevard frame, and each Boulevard page on its own, at phone/tablet/desktop.

    python3 -m http.server 8026 --bind 127.0.0.1          # from the repo root
    ~/.venvs/playwright/bin/python -I tests/flow.py [base-url]   # default http://localhost:8026/

Prints FAILS: none and exits 0 when everything works; screenshots go to tests/out/flow/.
"""
import os
import sys

from playwright.sync_api import sync_playwright

B = (sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8026/').rstrip('/') + '/'
L = B + "BOULEVARD/L'boulevard%2026/"
ROOMS = ['index.html', 'Band/index.html', 'Movement/index.html', 'Faces/index.html']
SIZES = {'mobile': (390, 844), 'tablet': (820, 1180), 'desktop': (1440, 900)}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'flow')
os.makedirs(OUT, exist_ok=True)

fails = []
def ok(cond, msg):
    if not cond:
        fails.append(msg)

with sync_playwright() as p:
    browser = p.chromium.launch()
    for vn, (w, h) in SIZES.items():
        pg = browser.new_page(viewport={'width': w, 'height': h})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('response', lambda r: r.status >= 400 and errs.append(f'{r.status} {r.url}'))
        mob = w <= 820  # the side menu folds into a burger below 820px

        def menu():
            if mob:
                pg.click('.burger')

        def home():
            pg.goto(B + 'index.html')
            pg.wait_for_selector('.home h1')

        home()
        pg.screenshot(path=f'{OUT}/home_{vn}.png')

        menu()
        t0 = pg.evaluate('document.documentElement.dataset.theme')
        pg.click('#theme')
        ok(pg.evaluate('document.documentElement.dataset.theme') != t0, f'{vn} home theme switch')

        home(); pg.click('.cta'); pg.wait_for_selector('main h2')
        ok('#photography/' in pg.url, f'{vn} CTA -> {pg.url}')
        home(); menu(); pg.click('.meta a[href="#about"]'); pg.wait_for_selector('.about')
        menu(); pg.click('.logo'); pg.wait_for_selector('.home h1')

        pg.click('.home [data-zoom]')
        ok(pg.locator('#lb.on').is_visible(), f'{vn} hero viewer opens')
        for key in ['Tab'] * 6 + ['Shift+Tab'] * 6:  # pf-qsm.29: focus must stay inside the open viewer
            pg.keyboard.press(key)
            ok(pg.evaluate('!!document.activeElement.closest("#lb")'), f'{vn} {key} leaves the open viewer')
        pg.keyboard.press('Escape')
        ok(not pg.locator('#lb.on').count(), f'{vn} viewer closes on Esc')

        # pf-qsm.29: links in closed menu sections must not take focus
        hidden = pg.evaluate('''[...document.querySelectorAll('#work a, #work button')]
            .filter(e => e.checkVisibility({visibilityProperty: true}) && e.closest('.list') && !e.closest('.open > .list')).length''')
        ok(hidden == 0, f'{vn} {hidden} links in closed menu sections can take focus')

        # pf-qsm.28: no page taller than the screen when there is nothing more to show
        for route in ['', '#photography/boulevard']:
            pg.goto(B + 'index.html' + route); pg.wait_for_timeout(600)
            extra = pg.evaluate('document.documentElement.scrollHeight - innerHeight')
            if route or w < 1440:
                ok(extra <= 0, f'{vn} index.html{route} is {extra}px taller than the screen')

        hrefs = pg.eval_on_selector_all('#work a[href^="#"]', 'as => as.map(a => a.getAttribute("href"))')
        ok(len(hrefs) > 0, f'{vn} no menu links found')
        for hr in hrefs:
            home(); menu()
            pg.click(f'[data-sec="{hr[1:].split("/")[0]}"]>.tog')
            a = pg.locator(f'#work a[href="{hr}"]').first
            g = a.locator('xpath=ancestor::li[contains(@class,"gsec")]')
            if g.count() and g.locator(':scope>.tog').count():
                g.locator(':scope>.tog').click()
            pg.wait_for_timeout(350)  # fold-out animation
            a.click()
            if 'boulevard' in hr:
                pg.frame_locator('.lbv iframe').locator('.pages a').first.wait_for()
                ok(pg.url.endswith(hr), f'{vn} {hr}')
                continue
            pg.wait_for_selector('main h2')
            ok(pg.url.endswith(hr), f'{vn} menu {hr} -> {pg.url}')
            n = pg.locator('main [data-zoom]').count()
            pg.locator('main [data-zoom]').first.click()
            ok(pg.locator('#lb.on').is_visible(), f'{vn} {hr} viewer opens')
            if not mob and n > 1:  # arrows are hidden on small screens
                pg.click('#lb-n')
                ok(pg.inner_text('#lb-c').startswith('2'), f'{vn} {hr} viewer next')
            pg.click('#lb-x')
            ok(not pg.locator('#lb.on').count(), f'{vn} {hr} viewer closes')

        # the exhibition inside the frame: every room button, and its theme switch reaching the portfolio
        pg.goto(B + 'index.html#photography/boulevard'); pg.wait_for_timeout(800)
        pg.screenshot(path=f'{OUT}/lbv_frame_{vn}.png')
        names = pg.frame_locator('.lbv iframe').locator('.pages a').all_inner_texts()
        for i, n in enumerate(names):
            pg.goto(B + 'index.html#photography/boulevard')
            f = pg.frame_locator('.lbv iframe'); f.locator('.pages a').first.wait_for()
            f.locator('.pages a').nth(i).click(); pg.wait_for_timeout(500)
            ok(pg.frames[1].url.endswith('index.html'), f'{vn} frame room {n} -> {pg.frames[1].url}')
        # pf-qsm.2: the room is kept in the address, so refresh and shared links reopen it
        for room in ['Movement', 'Band', 'Faces']:
            pg.goto(B + 'index.html#photography/boulevard')
            f = pg.frame_locator('.lbv iframe'); f.locator('.pages a').first.wait_for()
            f.locator(f'.pages a[href*="{room}/"]').first.click(); pg.wait_for_timeout(600)
            ok(pg.url.endswith(f'#photography/boulevard/{room}'), f'{vn} room {room} not in address: {pg.url}')
            pg.reload(); pg.wait_for_timeout(800)
            ok(f'/{room}/index.html' in pg.frames[1].url, f'{vn} refresh in {room} -> {pg.frames[1].url}')
        for hr in hrefs + ['#about']:
            pg.goto(B + 'index.html' + hr); pg.reload(); pg.wait_for_timeout(300)
            ok(pg.url.endswith(hr) and pg.locator('main section').count() == 1, f'{vn} refresh on {hr}')

        pg.goto(B + 'index.html#photography/boulevard')
        f = pg.frame_locator('.lbv iframe'); f.locator('#theme').wait_for(); pg.wait_for_timeout(300)
        b0 = pg.evaluate('document.body.dataset.lbv')
        f.locator('#theme').click(); pg.wait_for_timeout(200)
        ok(pg.evaluate('document.body.dataset.lbv') != b0, f'{vn} frame theme reaches the portfolio')
        f.locator('#theme').click()

        # each Boulevard page on its own
        for room in ROOMS:
            pg.goto(L + room); pg.wait_for_load_state('load')
            pg.screenshot(path=f"{OUT}/lbv_{room.split('/')[0].replace('.html', '')}_{vn}.png")
            links = pg.eval_on_selector_all('.pages a', 'as => as.map(a => a.href)')
            for i, href in enumerate(links):
                pg.goto(L + room); pg.wait_for_load_state('load')
                pg.locator('.pages a').nth(i).click(); pg.wait_for_load_state('load')
                ok(pg.url == href, f'{vn} {room} nav {i} -> {pg.url}')
            pg.goto(L + room); pg.wait_for_load_state('load')
            t0 = pg.evaluate('document.documentElement.dataset.theme')
            pg.click('#theme')
            ok(pg.evaluate('document.documentElement.dataset.theme') != t0, f'{vn} {room} theme switch')
            pg.click('#theme')
            for i in range(pg.locator('.handles a').count()):
                ok(pg.locator('.handles a').nth(i).get_attribute('href').startswith('https://'), f'{vn} {room} handle {i}')
            sx = pg.evaluate('document.documentElement.scrollWidth - innerWidth')
            ok(sx <= 0, f'{vn} {room} scrolls sideways by {sx}px')

        pg.goto(B + 'index.html')
        sx = pg.evaluate('document.documentElement.scrollWidth - innerWidth')
        ok(sx <= 0, f'{vn} home scrolls sideways by {sx}px')
        ok(not errs, f'{vn} errors: {errs[:5]}')
        print(f'{vn}: {len(hrefs)} menu links, {len(names)} rooms in the frame, {len(ROOMS)} Boulevard pages')
        pg.close()
    browser.close()

print('FAILS:', fails or 'none')
sys.exit(1 if fails else 0)
