"""pf-qsm.3: broken links, missing images, console and network clean.

Run:  ~/.venvs/playwright/bin/python -I tests/pf-qsm.3_links.py [base_url]
Default base_url is http://localhost:8027/. Exit code 1 if any error is found.
Read-only: it only loads pages and sends GET requests.
"""
import re, sys, pathlib
from urllib.parse import urljoin, urlsplit, unquote
from playwright.sync_api import sync_playwright

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8027/").rstrip("/") + "/"
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "tests/out/pf-qsm.3"
OUT.mkdir(parents=True, exist_ok=True)
WIDTHS = {"390": (390, 844), "1440": (1440, 900)}
LBV = "BOULEVARD/L'boulevard%2026/"
STANDALONE = [LBV + p for p in ("index.html", "Movement/index.html", "Band/index.html", "Faces/index.html")]
FONT_HOSTS = ("fonts.googleapis.com", "fonts.gstatic.com")
MAILTO = re.compile(r"^mailto:[^@\s]+@[^@\s]+\.[a-z]{2,}$", re.I)

errors, warnings = [], []
def err(view, w, msg): errors.append(f"[{w}] {view}: {msg}")
def warn(view, w, msg): warnings.append(f"[{w}] {view}: {msg}")
def same_origin(u): return urlsplit(u).netloc == urlsplit(BASE).netloc

# scroll the frame to the bottom in steps so every lazy image starts loading, then wait for all <img>
SCROLL = """async () => { const h = () => document.documentElement.scrollHeight;
  for (let y = 0; y < h(); y += innerHeight * .7) { scrollTo(0, y); await new Promise(r => setTimeout(r, 100)); }
  scrollTo(0, h());
  // horizontal strips (the film rows at 390 px): slide each one to its end too, as a swipe would
  for (const e of document.querySelectorAll('*')) if (e.scrollWidth > e.clientWidth + 1 && /auto|scroll/.test(getComputedStyle(e).overflowX)) {
    e.scrollIntoView({block: 'center'}); for (let x = 0; x <= e.scrollWidth; x += e.clientWidth * .7) { e.scrollLeft = x; await new Promise(r => setTimeout(r, 100)); } }
  await new Promise(r => setTimeout(r, 300)); }"""
WAIT_IMGS = """() => Promise.all([...document.images].filter(i => i.getAttribute('src')).map(i => i.complete ? 0 :
  new Promise(r => { i.addEventListener('load', r); i.addEventListener('error', r); setTimeout(r, 10000); })))"""
COLLECT = """() => ({
  imgs: [...document.images].filter(i => i.getAttribute('src')).map(i => ({src: i.currentSrc || i.src, w: i.naturalWidth,
        shown: !!(i.offsetWidth || i.offsetHeight || i.getClientRects().length), lazy: i.loading === 'lazy'})),
  hrefs: [...document.querySelectorAll('a[href], link[href]')].map(a => ({raw: a.getAttribute('href'), abs: a.href})),
  ids: [...document.querySelectorAll('[id]')].map(e => e.id),
  bgs: [...new Set([...document.querySelectorAll('*')].flatMap(e => [getComputedStyle(e).backgroundImage,
        getComputedStyle(e, '::before').backgroundImage, getComputedStyle(e, '::after').backgroundImage])
        .flatMap(b => [...b.matchAll(/url\\("?([^")]+)"?\\)/g)].map(m => m[1])))],
})"""

def views_from(page):
    page.goto(BASE + "index.html")
    work = page.evaluate("WORK.map(s => ({id: s.id, projects: s.projects.map(p => ({id: p.id, imgs: p.imgs || [], boulevard: !!p.boulevard}))}))")
    v = ["index.html", "index.html#about"]
    for s in work:
        for p in s["projects"]:
            v.append(f"index.html#{s['id']}/{p['id']}")
            if p["boulevard"]:
                v += [f"index.html#{s['id']}/{p['id']}/{r}" for r in ("Movement", "Band", "Faces")]
    return work, v + STANDALONE

checked = {}  # url -> status, so each link and background is fetched once
def status(ctx, url):
    if url not in checked:
        try: checked[url] = ctx.request.get(url, timeout=15000, max_redirects=5).status
        except Exception as e: checked[url] = f"no answer ({str(e).splitlines()[0][:80]})"
    return checked[url]

def check_view(ctx, view, w, routes, external):
    page = ctx.new_page()
    def on_console(m):
        if m.type == "error": err(view, w, f"console.error: {m.text[:200]}")
    page.on("console", on_console)
    page.on("pageerror", lambda e: err(view, w, f"JS error: {e}"))
    def on_failed(r):
        (err if same_origin(r.url) else warn)(view, w, f"request failed: {r.url} ({r.failure})")
    page.on("requestfailed", on_failed)
    page.on("response", lambda r: r.status >= 400 and (err if same_origin(r.url) else warn)(view, w, f"HTTP {r.status}: {r.url}"))
    page.goto(BASE + view, wait_until="load")
    page.wait_for_timeout(400)
    frames = [page.main_frame] + [f for f in page.frames if f != page.main_frame]
    if view.startswith("index.html#photography/boulevard"):
        if len(frames) < 2: err(view, w, "the exhibition iframe did not load")
        else: frames[1].wait_for_load_state("load")
    bad_before = len(errors)
    for f in frames:
        where = "" if f == page.main_frame else " (in iframe)"
        f.evaluate(SCROLL); f.evaluate(WAIT_IMGS)
        d = f.evaluate(COLLECT)
        for i in d["imgs"]:
            if i["w"] == 0:
                if i["shown"] or not i["lazy"]: err(view, w, f"image not loaded{where}: {i['src']}")
                else: warn(view, w, f"hidden lazy image never loaded{where}: {i['src']}")
        for b in d["bgs"]:
            s = status(ctx, b) if b.startswith("http") else 200
            if s != 200: err(view, w, f"CSS background image{where} returns {s}: {b}")
        for h in d["hrefs"]:
            raw, url = h["raw"], h["abs"]
            if raw.startswith("mailto:"):
                if not MAILTO.match(raw): err(view, w, f"bad mailto: {raw}")
            elif url.startswith(("http:", "https:")) and same_origin(url):
                s = status(ctx, url.split("#")[0])
                if s != 200: err(view, w, f"link{where} {raw!r} -> {url} returns {s}")
                frag = urlsplit(url).fragment
                if frag and url.split("#")[0] == f.url.split("#")[0]:
                    # same document: on the homepage a hash is a route, elsewhere it must be an element id
                    if f == page.main_frame and urlsplit(f.url).path.endswith(("/", "index.html")) and "BOULEVARD" not in f.url:
                        if frag not in routes: err(view, w, f"link {raw!r} is not a known route")
                    elif unquote(frag) not in d["ids"]: err(view, w, f"link{where} {raw!r}: no element with that id")
            elif url.startswith(("http:", "https:")):
                external.add(url)
            else: err(view, w, f"unexpected href{where}: {raw}")
    if len(errors) > bad_before:
        page.screenshot(path=str(OUT / f"{re.sub(r'[^A-Za-z0-9]+', '_', view)}_{w}.png"))
    page.close()

def fonts_blocked(browser):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    ctx.route(re.compile(r"https://(fonts\.googleapis\.com|fonts\.gstatic\.com)/.*"), lambda r: r.abort())
    page = ctx.new_page(); view, w = "home, Google Fonts blocked", "1440"
    page.on("pageerror", lambda e: err(view, w, f"JS error: {e}"))
    # the blocked font requests log "Failed to load resource" by design; anything else is a real error
    page.on("console", lambda m: m.type == "error" and not any(h in m.text + m.location.get("url", "") for h in FONT_HOSTS) and err(view, w, f"console.error: {m.text[:200]}"))
    page.on("requestfailed", lambda r: not any(h in r.url for h in FONT_HOSTS) and err(view, w, f"request failed: {r.url}"))
    page.goto(BASE + "index.html", wait_until="load"); page.wait_for_timeout(800)
    info = page.evaluate("""() => { const h = document.querySelector('h1'), r = h && h.getBoundingClientRect();
      return {h1: r ? [r.width, r.height] : null, webfonts_loaded: [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family), family: getComputedStyle(document.body).fontFamily,
              img: (document.querySelector('.home img') || {}).naturalWidth || 0}; }""")
    if not info["h1"] or info["h1"][1] < 10: err(view, w, f"headline not rendered: {info}")
    if not info["img"]: err(view, w, "home photo not loaded")
    page.screenshot(path=str(OUT / "home_fonts-blocked_1440.png"))
    ctx.close()
    return info

def check_assets(work):
    files = {p.stem for p in (ROOT / "assets/home").glob("*.jpg")}
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    used = {i for s in work for p in s["projects"] for i in p["imgs"]}
    for i in sorted(used - files): err("WORK array", "-", f"image id {i} has no file assets/home/{i}.jpg")
    # a file is used if its name appears anywhere in index.html (s23 is used by the home view, outside WORK)
    unused = sorted(f for f in files - used if f not in html)
    return len(used), len(files), unused

with sync_playwright() as pw:
    browser = pw.chromium.launch()
    external = set()
    for w, (vw, vh) in WIDTHS.items():
        ctx = browser.new_context(viewport={"width": vw, "height": vh})
        p0 = ctx.new_page(); work, views = views_from(p0); p0.close()
        routes = {""} | {v.split("#", 1)[1] for v in views if "#" in v}
        for v in views: check_view(ctx, v, w, routes, external)
        ext_status = {u: status(ctx, u) for u in sorted(external)}
        ctx.close()
    font_info = fonts_blocked(browser)
    browser.close()

n_used, n_files, unused = check_assets(work)
print(f"views: {len(views)} x {len(WIDTHS)} widths   base: {BASE}")
print(f"WORK image ids: {n_used}, files in assets/home: {n_files}")
print("files in assets/home that nothing in index.html references:", ", ".join(unused) or "none")
print("fonts blocked:", font_info)
print("\nexternal links (not a failure):")
for u, s in ext_status.items(): print(f"  {s}  {u}")
print(f"\nwarnings ({len(set(warnings))}):"); [print("  " + x) for x in sorted(set(warnings))]
print(f"\nERRORS ({len(set(errors))}):"); [print("  " + x) for x in sorted(set(errors))]
print("\nFAIL" if errors else "\nPASS")
sys.exit(1 if errors else 0)
