"""pf-qsm.19: full-page screenshots of every view, before/after a change.

Usage:  ~/.venvs/playwright/bin/python -I tests/pf-qsm.19_screens.py before|after [base_url]
Writes tests/screens/<before|after>/<view>_<theme>_<width>.png and rebuilds tests/screens/index.html.
"""
import html, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

WIDTHS = [(390, 844), (820, 1180), (1440, 900)]
THEMES = ['light', 'dark']
LBV = "assets/boulevard/"
OUT = Path(__file__).resolve().parent / 'screens'

# no transitions/animations, so colours and fades are final when we shoot
NO_MOTION = '*,*::before,*::after{transition:none!important;animation:none!important}'
SETTLE = """async () => {
  const docs = [document, ...[...document.querySelectorAll('iframe')].map(f => { try { return f.contentDocument; } catch (e) { return null; } }).filter(Boolean)];
  for (const d of docs) d.querySelectorAll('img[loading=lazy]').forEach(i => i.loading = 'eager');
  const imgs = docs.flatMap(d => [...d.images]);
  await Promise.all(imgs.map(i => i.complete ? 0 : new Promise(r => { i.addEventListener('load', r); i.addEventListener('error', r); setTimeout(r, 15000); })));
  await Promise.all(docs.map(d => d.fonts && d.fonts.ready));
}"""


def views(page, base):
    """[(name, url)] from the live WORK array, plus the standalone exhibition pages."""
    page.goto(base + 'index.html')
    routes = page.evaluate("""() => WORK.flatMap(s => s.projects.flatMap(p =>
        [`${s.id}/${p.id}`, ...(p.doors || []).map(d => `${s.id}/${p.id}/${d[1]}`)]))""")
    out = [('home', base + 'index.html#'), ('about', base + 'index.html#about')]
    out += [(r.replace('/', '_'), base + 'index.html#' + r) for r in routes]
    out += [('lbv-hub', base + LBV + 'index.html')]
    out += [('lbv-' + room, f'{base}{LBV}{room}/index.html') for room in ('Movement', 'Band', 'Faces')]
    return out


def shoot(phase, base):
    d = OUT / phase
    d.mkdir(parents=True, exist_ok=True)
    n = 0
    with sync_playwright() as p:
        b = p.chromium.launch()
        vs = views(b.new_page(), base)
        for theme in THEMES:
            for w, h in WIDTHS:
                ctx = b.new_context(viewport={'width': w, 'height': h}, color_scheme=theme)
                ctx.add_init_script(f"try{{localStorage.setItem('skm-theme','{theme}');localStorage.setItem('lbv-theme','{theme}')}}catch(e){{}}")
                ctx.add_init_script(f"addEventListener('DOMContentLoaded',()=>{{const s=document.createElement('style');s.textContent='{NO_MOTION}';document.head.append(s)}})")
                page = ctx.new_page()
                for name, url in vs:
                    page.goto('about:blank')  # a fresh load for each hash route
                    page.goto(url, wait_until='load')
                    page.evaluate(SETTLE)
                    page.wait_for_timeout(300)
                    page.screenshot(path=str(d / f'{name}_{theme}_{w}.png'), full_page=True)
                    n += 1
                    print(f'{phase} {name} {theme} {w}', flush=True)
                ctx.close()
        b.close()
    return vs, n


def gallery(vs):
    rows, toc = [], []
    for name, url in vs:
        toc.append(f'<a href="#{name}">{name}</a>')
        rows.append(f'<h2 id="{name}">{name} <a class="u" href="{html.escape(url)}">{html.escape(url)}</a></h2>')
        for theme in THEMES:
            for w, _ in WIDTHS:
                f = f'{name}_{theme}_{w}.png'
                cell = lambda ph: (f'<a href="{ph}/{f}"><img loading="lazy" src="{ph}/{f}" alt="{ph} {f}"></a>'
                                   if (OUT / ph / f).exists() else '<span class="none">not taken yet</span>')
                rows.append(f'<div class="row" data-t="{theme}" data-w="{w}"><p>{name} · {theme} · {w}px</p>'
                            f'<div class="pair"><div><b>before</b>{cell("before")}</div><div><b>after</b>{cell("after")}</div></div></div>')
    filt = lambda k, vals: f'<select data-k="{k}"><option value="">all</option>' + ''.join(f'<option>{v}</option>' for v in vals) + '</select>'
    (OUT / 'index.html').write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Before / after</title>
<style>
body{{margin:0;padding:16px;font:14px/1.4 system-ui,sans-serif;background:#f4f2ee;color:#111}}
header{{position:sticky;top:0;background:#f4f2ee;padding:8px 0;border-bottom:1px solid #ccc;z-index:1}}
nav{{display:flex;gap:10px;margin-top:6px;font-size:12px;overflow-x:auto;white-space:nowrap;padding-bottom:4px}}
h2{{font-size:16px;margin:28px 0 6px}} .u{{font-size:11px;font-weight:400;word-break:break-all;color:#666}}
.row p{{margin:12px 0 4px;color:#555}} .pair{{display:grid;grid-template-columns:1fr 1fr;gap:8px}}
.pair b{{display:block;font-size:11px;text-transform:uppercase;color:#888}}
.pair img{{width:100%;max-height:1400px;object-fit:cover;object-position:top;border:1px solid #ccc;background:#fff}}
.none{{display:block;padding:24px;border:1px dashed #bbb;color:#999;text-align:center}}
</style></head><body>
<header><b>pf-qsm.19 before / after</b> · theme {filt('t', THEMES)} width {filt('w', [w for w, _ in WIDTHS])}
<nav>{''.join(toc)}</nav></header>
{''.join(rows)}
<script>
const sel = [...document.querySelectorAll('select')];
const apply = () => document.querySelectorAll('.row').forEach(r => r.hidden = sel.some(s => s.value && r.dataset[s.dataset.k] !== s.value));
sel.forEach(s => s.onchange = apply);
</script></body></html>""")


if __name__ == '__main__':
    phase = sys.argv[1] if len(sys.argv) > 1 else ''
    assert phase in ('before', 'after'), 'usage: pf-qsm.19_screens.py before|after [base_url]'
    base = (sys.argv[2] if len(sys.argv) > 2 else 'http://localhost:8027/').rstrip('/') + '/'
    vs, n = shoot(phase, base)
    gallery(vs)
    print(f'{n} screenshots in {OUT / phase}; gallery: {OUT / "index.html"}')
