"""pf-qsm.13 content check: per page/view title, share tags, icons, lang, and alt texts.
Run: ~/.venvs/playwright/bin/python -I tests/pf-qsm.13_content.py [base]   (default http://localhost:8027/)
Writes tests/out/pf-qsm.13/content.json and prints a summary. Read-only on the site."""
import json, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = (sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8027/').rstrip('/') + '/'
LBV = "assets/boulevard/"
PAGES = ['index.html', LBV + 'index.html', LBV + 'Movement/index.html', LBV + 'Band/index.html', LBV + 'Faces/index.html']
TAGS = ['meta[name=description]', 'meta[property="og:title"]', 'meta[property="og:description"]', 'meta[property="og:image"]',
        'meta[property="og:url"]', 'meta[name="twitter:card"]', 'link[rel~=icon]', 'link[rel=apple-touch-icon]']
GENERIC = re.compile(r'^(.*, )?(photo|poster|image|picture) \d+$', re.I)
OUT = Path(__file__).parent / 'out' / 'pf-qsm.13'

def scan(page):
    head = page.evaluate("""tags => ({title: document.title, lang: document.documentElement.lang,
        tags: Object.fromEntries(tags.map(s => [s, !!document.querySelector(s)]))})""", TAGS)
    imgs = page.evaluate("""() => [...document.querySelectorAll('img')].filter(i => !i.closest('[aria-hidden=true]') && !i.closest('[role=dialog]'))
        .map(i => ({src: i.getAttribute('src'), alt: i.getAttribute('alt')}))""")
    head['imgs'] = len(imgs)
    head['missing_alt'] = [i['src'] for i in imgs if i['alt'] is None or not i['alt'].strip()]
    head['generic_alt'] = [i['alt'] for i in imgs if i['alt'] and GENERIC.match(i['alt'])]
    return head

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    res = {}
    with sync_playwright() as p:
        b = p.chromium.launch(); page = b.new_page(viewport={'width': 1440, 'height': 900})
        for u in PAGES:
            page.goto(BASE + u); page.wait_for_load_state('networkidle'); res[u] = scan(page)
        # homepage views: one per project link in the side menu, plus #about
        page.goto(BASE + 'index.html')
        hashes = ['#about'] + page.eval_on_selector_all('#work a[href^="#"]', 'as => as.map(a => a.getAttribute("href"))')
        for h in hashes:
            page.goto(BASE + 'index.html' + h); page.wait_for_timeout(150)
            if 'boulevard' in h: continue  # the exhibition is checked above as its own pages
            res['index.html' + h] = scan(page)
        b.close()
    (OUT / 'content.json').write_text(json.dumps(res, indent=1, ensure_ascii=False))
    gen = sum(len(v['generic_alt']) for v in res.values()); miss = sum(len(v['missing_alt']) for v in res.values())
    for k, v in res.items():
        absent = [t for t, ok in v['tags'].items() if not ok]
        print(f"{k}\n  title={v['title']!r} lang={v['lang']!r} imgs={v['imgs']} generic={len(v['generic_alt'])} missing={len(v['missing_alt'])}"
              + (f"\n  no: {', '.join(absent)}" if absent else ''))
    print(f'TOTAL generic alts: {gen}, missing alts: {miss}')
    assert all(v['lang'] for v in res.values()), 'a page has no lang'

if __name__ == '__main__':
    main()
