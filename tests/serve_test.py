"""scripts/serve.py on a throw-away copy of the site: what it refuses, then the page editor saving through it.

    ~/.venvs/playwright/bin/python -I tests/serve_test.py
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8097
B = f'http://localhost:{PORT}/'
FAILS = []
ok = lambda c, m: c or FAILS.append(m)

tmp = tempfile.mkdtemp(prefix='skimart-serve-')
for d in ['assets/home', 'assets/archive', 'data', 'tools']:
    shutil.copytree(os.path.join(ROOT, d), os.path.join(tmp, d))
shutil.copy(os.path.join(ROOT, 'index.html'), tmp)
srv = subprocess.Popen([sys.executable, '-I', os.path.join(ROOT, 'scripts/serve.py'), str(PORT)], env={**os.environ, 'SKIMART_ROOT': tmp},
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def call(method, path, body=b'x', headers=None):
    req = urllib.request.Request(B + path, data=body if method == 'PUT' else None, method=method, headers=headers or {})
    try:
        return urllib.request.urlopen(req).status
    except urllib.error.HTTPError as e:
        return e.code


try:
    for _ in range(50):
        try: urllib.request.urlopen(B + '__can-save'); break
        except OSError: time.sleep(.1)
    SAVE = {'X-Skimart-Save': '1', 'Origin': B.rstrip('/')}
    ok(call('GET', '__can-save') == 204, 'the tools can ask whether saving works')
    ok(call('GET', 'index.html') == 200, 'serves the site')
    ok(call('PUT', 'data/photos.json', headers={'Origin': B.rstrip('/')}) == 403, 'no save header: refused')
    ok(call('PUT', 'data/photos.json', headers={'X-Skimart-Save': '1', 'Origin': 'https://evil.example'}) == 403, 'another site: refused')
    for bad in ['scripts/serve.py', 'assets/home/../x.jpg', 'assets/home/%2e%2e/x.jpg', 'data/taxonomy.json', 'tools/pages.js', 'assets/home/x.png']:
        ok(call('PUT', bad, headers=SAVE) == 403, f'{bad}: refused')
    ok(call('PUT', 'assets/home/t/zz-test.jpg', body=b'jpg', headers=SAVE) == 204 and open(os.path.join(tmp, 'assets/home/t/zz-test.jpg'), 'rb').read() == b'jpg', 'writes an allowed file')
    ok(call('DELETE', 'assets/home/t/zz-test.jpg', headers=SAVE) == 204 and not os.path.exists(os.path.join(tmp, 'assets/home/t/zz-test.jpg')), 'deletes it')

    orig = json.loads('[' + re.search(r"\{id:'soualem'.*?imgs:\[(.*?)\]", open(os.path.join(tmp, 'index.html'), encoding='utf-8').read()).group(1) + ']')
    with sync_playwright() as p:
        pg = p.chromium.launch().new_page(viewport={'width': 1440, 'height': 900})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.add_init_script('delete window.showDirectoryPicker')  # the server is the only way to save here
        pg.goto(B + 'tools/pages.html'); pg.wait_for_selector('.tiles li')
        pg.select_option('#page', 'photography|soualem|'); pg.wait_for_timeout(200)
        pg.locator('.tiles li[data-i="0"] [data-a="right"]').click()
        pg.locator('.tiles li[data-i="1"] [data-a="x"]').click()
        pg.click('#save'); pg.wait_for_function("document.getElementById('status').textContent === 'saved' || document.getElementById('errors').textContent")
        ok(pg.text_content('#errors') == '', 'save error: ' + pg.text_content('#errors'))
        ok(not errs, f'page errors: {errs}')
    html = open(os.path.join(tmp, 'index.html'), encoding='utf-8').read()
    saved = json.loads('[' + re.search(r"\{id:'soualem'.*?imgs:\[(.*?)\]", html).group(1) + ']')
    ok(saved == [orig[1]] + orig[2:], 'order saved to disk through the server')
    ok(not os.path.exists(os.path.join(tmp, f'assets/home/{orig[0]}.jpg')), 'removed photo file deleted on disk')
    ok(orig[0] not in open(os.path.join(tmp, 'data/photos.json'), encoding='utf-8').read(), 'removed photo out of the archive on disk')
    ok(not [f for r, _, fs in os.walk(tmp) for f in fs if f.endswith('.part')], 'no half-written files left')
finally:
    srv.terminate(); srv.wait(); shutil.rmtree(tmp)

print('FAILS:', FAILS or 'none')
sys.exit(1 if FAILS else 0)
