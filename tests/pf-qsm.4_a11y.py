"""pf-qsm.4 accessibility audit: axe-core on every view x theme x width, plus hand checks
(alt texts, visible focus, viewer focus trap, tap targets, headings, lang/title).

Run:  ~/.venvs/playwright/bin/python -I tests/pf-qsm.4_a11y.py [base-url]
      (default http://localhost:8027/). Writes tests/out/pf-qsm.4/; exit 1 on serious/critical axe violations.
"""
import json, re, sys, urllib.request
from collections import defaultdict
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8027/").rstrip("/") + "/"
HERE = Path(__file__).resolve().parent
OUT = HERE / "out" / "pf-qsm.4"
AXE = HERE / "out" / "axe.min.js"
AXE_URL = "https://cdn.jsdelivr.net/npm/axe-core@4.10.2/axe.min.js"
LBV = "assets/boulevard/"
HOME_VIEWS = ["", "#about", "#photography/jazz", "#design/personal", "#workshops/poster-making", "#photography/boulevard"]
EXHIBITS = {"lbv-hub": LBV + "index.html", "lbv-movement": LBV + "Movement/index.html",
            "lbv-band": LBV + "Band/index.html", "lbv-faces": LBV + "Faces/index.html"}
WIDTHS = {390: 844, 1440: 900}
THEMES = ["light", "dark"]
AXE_OPTS = {"runOnly": {"type": "tag", "values": ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "best-practice"]},
            "iframes": False}

# --- in-page helpers -------------------------------------------------------------
JS_VISIBLE = """
window.__vis = el => {  // visible area of el after clipping by overflow ancestors (0 = user cannot see it)
  let r = el.getBoundingClientRect(); if (!r.width || !r.height) return 0;
  let L = r.left, T = r.top, R = r.right, B = r.bottom;
  for (let a = el.parentElement; a; a = a.parentElement) {
    const cs = getComputedStyle(a);
    if (cs.display === 'none' || cs.visibility === 'hidden') return 0;
    if (/(hidden|clip|auto|scroll)/.test(cs.overflow)) { const q = a.getBoundingClientRect();
      L = Math.max(L, q.left); T = Math.max(T, q.top); R = Math.min(R, q.right); B = Math.min(B, q.bottom); }
  }
  return Math.max(0, R - L) * Math.max(0, B - T);
};
window.__desc = el => { if (!el || el === document.body) return 'body';
  const id = el.id ? '#' + el.id : '', cls = (el.className && el.className.baseVal === undefined && el.className) ? '.' + el.className.trim().split(/\\s+/).join('.') : '';
  const name = (el.getAttribute('aria-label') || el.textContent || '').trim().replace(/\\s+/g, ' ').slice(0, 40);
  return `${el.tagName.toLowerCase()}${id}${cls} "${name}"`; };
"""
JS_FACTS = """() => {
  const vis = e => window.__vis(e) > 0;
  const imgs = [...document.querySelectorAll('img')].filter(i => !i.closest('[aria-hidden="true"]') && i.getAttribute('alt') !== '' && vis(i))
    .map(i => ({src: i.getAttribute('src').split('/').pop(), alt: i.getAttribute('alt'), named_by_parent: !!i.closest('[aria-label]')}));
  const heads = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter(h => !h.closest('[hidden]'))
    .map(h => ({level: +h.tagName[1], text: (h.getAttribute('aria-label') || h.textContent).trim().replace(/\\s+/g, ' ').slice(0, 50)}));
  const sel = 'a[href],button,[tabindex]:not([tabindex="-1"]),[role=button]';
  const targets = [...document.querySelectorAll(sel)].filter(e => vis(e) && !e.closest('[inert]')).map(e => {
    const r = e.getBoundingClientRect(), cs = getComputedStyle(e);
    const inline = cs.display === 'inline' && !!e.closest('p,dd,li') && (e.parentElement.textContent.trim().length > e.textContent.trim().length + 5);
    return {el: window.__desc(e), w: Math.round(r.width), h: Math.round(r.height), inline};
  }).filter(t => t.w < 44 || t.h < 44);
  return {lang: document.documentElement.lang, title: document.title, imgs, heads, small_targets: targets};
}"""
# axe skips text contrast on the exhibition pages (and misses the homepage menu counts) (the film-grain ::after sits on top of everything), so measure it here:
# text colour (alpha and opacity blended) against the first solid background behind it; the grain itself is ignored.
JS_CONTRAST = """() => {
  const rgb = s => { const m = s.match(/[\\d.]+/g).map(Number); return [m[0], m[1], m[2], m.length > 3 ? m[3] : 1]; };
  const mix = (f, b) => [0, 1, 2].map(i => f[i] * f[3] + b[i] * (1 - f[3])).concat(1);
  const lum = c => { const l = c.slice(0, 3).map(v => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; });
    return .2126 * l[0] + .7152 * l[1] + .0722 * l[2]; };
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05); };
  const bgOf = el => { const layers = [];
    for (let a = el; a; a = a.parentElement) { const c = rgb(getComputedStyle(a).backgroundColor); if (c[3] > 0) { layers.push(c); if (c[3] === 1) break; } }
    let b = [255, 255, 255, 1]; for (const c of layers.reverse()) b = mix(c, b); return b; };
  const out = {}, zoom = parseFloat(getComputedStyle(document.documentElement).zoom) || 1;
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let t; (t = walker.nextNode());) {
    const el = t.parentElement; if (!t.textContent.trim() || !el || el.closest('[hidden],svg') || !window.__vis(el)) continue;
    const cs = getComputedStyle(el); if (cs.visibility === 'hidden') continue;
    let op = 1; for (let a = el; a; a = a.parentElement) op *= parseFloat(getComputedStyle(a).opacity);
    if (op < .05) continue;
    const bg = bgOf(el), fc = rgb(cs.color); if (!fc[3]) continue;  // outline-only numerals (text-stroke) are decoration
    fc[3] *= op;
    const r = ratio(mix(fc, bg), bg), px = parseFloat(cs.fontSize) * zoom, bold = parseInt(cs.fontWeight) >= 700;
    const need = (px >= 24 || (bold && px >= 18.66)) ? 3 : 4.5;
    if (r < need) { const k = window.__desc(el).replace(/ ".*/, '') + ' ' + cs.color;
      out[k] = out[k] || {el: window.__desc(el), color: cs.color, bg: 'rgb(' + bg.slice(0, 3).map(Math.round) + ')', ratio: +r.toFixed(2), px: +px.toFixed(1), need, count: 0};
      out[k].count++; } }
  return Object.values(out);
}"""
JS_FOCUS_INFO = """() => { const e = document.activeElement; if (!e || e === document.body) return null;
  const r = e.getBoundingClientRect();
  return {el: window.__desc(e), vis: window.__vis(e), x: r.left, y: r.top, w: r.width, h: r.height, iframe: e.tagName === 'IFRAME',
          key: e.tagName + '|' + (e.id || '') + '|' + (e.getAttribute('href') || '') + '|' + (e.getAttribute('aria-label') || e.textContent.trim().slice(0, 30))}; }"""


def ensure_axe():
    if not AXE.exists():
        AXE.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(AXE_URL, AXE)


def new_page(browser, theme, w):
    ctx = browser.new_context(viewport={"width": w, "height": WIDTHS[w]}, reduced_motion="no-preference")
    ctx.add_init_script(f"try{{localStorage.setItem('skm-theme','{theme}');localStorage.setItem('lbv-theme','{theme}')}}catch(e){{}}")
    ctx.add_init_script(JS_VISIBLE)
    page = ctx.new_page()
    page.on("pageerror", lambda e: print("  pageerror:", e))
    return ctx, page


def go(page, url):
    page.goto("about:blank")  # hash-only changes would not reload the homepage, and menu state would carry over
    page.goto(url, wait_until="load")
    page.wait_for_timeout(1000)  # colour transitions (.4s) and image fade-ins finish before contrast is measured


def run_axe(frame):
    if not frame.evaluate("typeof axe !== 'undefined'"):
        frame.add_script_tag(path=str(AXE))
    res = frame.evaluate("opts => axe.run(document, opts)", AXE_OPTS)
    return [{"id": v["id"], "impact": v["impact"], "help": v["help"], "tags": v["tags"], "url": v["helpUrl"],
             "nodes": [{"target": n["target"], "html": n["html"][:200], "summary": n["failureSummary"][:300]} for n in v["nodes"]]}
            for v in res["violations"]]


def open_viewer(page, homepage):
    page.locator("[data-zoom]" if homepage else ".shot").first.click()
    page.wait_for_timeout(700)


def viewer_trap(page, homepage, presses=12):
    """Tab from inside the open viewer; return the elements focus reached outside it."""
    box = "#lb" if homepage else "#viewer"
    escaped = []
    for i in range(presses):
        page.keyboard.press("Tab")
        info = page.evaluate(f"() => {{ const e = document.activeElement; return {{inside: !!e.closest('{box}'), el: window.__desc(e)}}; }}")
        if not info["inside"]:
            escaped.append({"press": i + 1, "el": info["el"]})
    return escaped


def focus_walk(page, shot_dir, max_stops=140):
    """Tab through the page. For each stop: is it visible, and does focus change any pixel around it?"""
    page.evaluate("() => { document.activeElement && document.activeElement.blur(); window.scrollTo(0, 0); }")
    seen, problems, stops = set(), [], 0
    for _ in range(max_stops):
        page.keyboard.press("Tab")
        page.wait_for_timeout(60)
        f = page.evaluate(JS_FOCUS_INFO)
        if not f:
            break
        if f["key"] in seen:
            break  # wrapped round
        seen.add(f["key"]); stops += 1
        if f["iframe"]:
            continue
        if f["vis"] == 0:
            problems.append({"el": f["el"], "issue": "focus lands on an element the user cannot see (hidden or clipped)"})
            continue
        vw, vh = page.viewport_size["width"], page.viewport_size["height"]
        x, y = max(0, f["x"] - 8), max(0, f["y"] - 8)
        w, h = min(vw - x, f["w"] + 16), min(vh - y, f["h"] + 16)
        if w < 2 or h < 2:
            continue
        clip = {"x": x, "y": y, "width": w, "height": h}
        on = page.screenshot(clip=clip, animations="disabled")
        page.evaluate("() => { window.__last = document.activeElement; document.activeElement.blur(); }")
        off = page.screenshot(clip=clip, animations="disabled")
        page.evaluate("() => window.__last.focus({focusVisible: true, preventScroll: true})")
        if on == off:
            problems.append({"el": f["el"], "issue": "no visible change when the element gets keyboard focus"})
            (shot_dir / f"nofocus_{len(problems):02d}.png").write_bytes(on)
    return stops, problems


def generic_alt(a):
    return bool(re.search(r",\s*(photo|poster)\s*\d+$", a["alt"], re.I)) or len(a["alt"].split()) < 3


def main():
    ensure_axe()
    OUT.mkdir(parents=True, exist_ok=True)
    results = {"base": BASE, "axe": [], "facts": [], "focus": [], "trap": [], "contrast": []}
    with sync_playwright() as p:
        br = p.chromium.launch()
        jobs = [("home" + (v.replace("#", "-").replace("/", "-") if v else ""), BASE + "index.html" + v, True, v) for v in HOME_VIEWS]
        jobs += [(k, BASE + u, False, None) for k, u in EXHIBITS.items()]
        for theme in THEMES:
            for w in WIDTHS:
                ctx, page = new_page(br, theme, w)
                for name, url, homepage, hv in jobs:
                    go(page, url)
                    tag = {"view": name, "theme": theme, "width": w}
                    print(f"{name:32s} {theme:5s} {w}")
                    results["axe"].append({**tag, "frame": "top", "violations": run_axe(page)})
                    results["facts"].append({**tag, **page.evaluate(JS_FACTS)})
                    results["contrast"].append({**tag, "fails": page.evaluate(JS_CONTRAST)})
                    if hv == "#photography/boulevard":
                        fr = page.locator("iframe").element_handle().content_frame()
                        fr.wait_for_load_state("load"); page.wait_for_timeout(800)
                        results["axe"].append({**tag, "frame": "exhibition iframe", "violations": run_axe(fr)})
                    page.screenshot(path=str(OUT / f"{name}_{theme}_{w}.png"))
                    has_viewer = hv not in ("#about", "#photography/boulevard") if homepage else name != "lbv-hub"
                    if has_viewer:
                        open_viewer(page, homepage)
                        vtag = {**tag, "view": name + " +viewer"}
                        results["axe"].append({**vtag, "frame": "top", "violations": run_axe(page)})
                        results["facts"].append({**vtag, **page.evaluate(JS_FACTS)})
                        results["contrast"].append({**vtag, "fails": page.evaluate(JS_CONTRAST)})
                        page.screenshot(path=str(OUT / f"{name}_viewer_{theme}_{w}.png"))
                        if w == 1440:
                            results["trap"].append({**vtag, "escaped": viewer_trap(page, homepage)})
                        page.keyboard.press("Escape"); page.wait_for_timeout(300)
                        back = page.evaluate("() => window.__desc(document.activeElement)")
                        if w == 1440:
                            results["trap"].append({**vtag, "focus_after_escape": back})
                    if w == 1440 and hv != "#photography/boulevard":
                        d = OUT / "focus" / f"{name}_{theme}"; d.mkdir(parents=True, exist_ok=True)
                        go(page, url)
                        stops, probs = focus_walk(page, d)
                        results["focus"].append({**tag, "stops": stops, "problems": probs})
                ctx.close()
        br.close()

    (OUT / "results.json").write_text(json.dumps(results, indent=1))

    # --- summary: one line per rule, with where it hits --------------------------
    rules = defaultdict(lambda: {"where": set(), "nodes": set(), "impact": None, "help": ""})
    for r in results["axe"]:
        for v in r["violations"]:
            k = rules[v["id"]]; k["impact"], k["help"] = v["impact"], v["help"]
            k["where"].add(f'{r["view"]}{" (iframe)" if r["frame"] != "top" else ""} {r["theme"]} {r["width"]}')
            k["nodes"].update(" > ".join(map(str, n["target"])) for n in v["nodes"])
    order = {"critical": 0, "serious": 1, "moderate": 2, "minor": 3}
    lines = ["AXE (unique rules):"]
    for rid, k in sorted(rules.items(), key=lambda x: order.get(x[1]["impact"], 9)):
        lines.append(f'  [{k["impact"]}] {rid}: {k["help"]} — {len(k["nodes"])} elements, {len(k["where"])} runs')
        lines += [f"      e.g. {n}" for n in sorted(k["nodes"])[:4]]
    lines.append("FOCUS:")
    for f in results["focus"]:
        if f["problems"]:
            lines.append(f'  {f["view"]} {f["theme"]}: {len(f["problems"])}/{f["stops"]} stops — ' +
                         "; ".join(sorted({p["issue"] for p in f["problems"]})))
            lines += [f'      {p["el"]}' for p in f["problems"][:6]]
    lines.append("VIEWER FOCUS TRAP (1440):")
    lines += [f'  {t["view"]} {t["theme"]}: ' + (f'escaped {len(t["escaped"])}/12 Tabs, first to {t["escaped"][0]["el"]}' if t.get("escaped") else
              ("stays inside" if "escaped" in t else f'after Escape focus is on {t["focus_after_escape"]}')) for t in results["trap"]]
    lines.append("TEXT CONTRAST measured by hand (axe cannot see through the exhibition grain, and skips some homepage text):")
    for c in results["contrast"]:
        for f in c["fails"]:
            lines.append(f'  {c["view"]} {c["theme"]} {c["width"]}: {f["el"]} {f["color"]} on {f["bg"]} = {f["ratio"]} (need {f["need"]}, {f["px"]}px, x{f["count"]})')
    lines.append("ALT / HEADINGS / TITLE / TAP TARGETS (dark 390 + dark 1440):")
    for f in results["facts"]:
        if f["theme"] != "dark":
            continue
        g = [a["alt"] for a in f["imgs"] if generic_alt(a)]
        hl = [h["level"] for h in f["heads"]]
        skips = [f"h{a}->h{b}" for a, b in zip(hl, hl[1:]) if b > a + 1]
        small = [t for t in f["small_targets"] if not t["inline"]]
        lines.append(f'  {f["view"]} {f["width"]}: lang={f["lang"]!r} title={f["title"]!r} h1={hl.count(1)} skips={skips} '
                     f'generic-alt={len(g)}/{len(f["imgs"])} small-targets={len(small)} (<24px: {sum(1 for t in small if min(t["w"], t["h"]) < 24)})')
        if f["width"] == 390:
            lines += [f'      small: {t["el"]} {t["w"]}x{t["h"]}' for t in small[:8]]
        if g:
            lines.append(f"      alt e.g. {g[:3]}")
    (OUT / "summary.txt").write_text("\n".join(lines))
    print("\n".join(lines))

    bad = [rid for rid, k in rules.items() if k["impact"] in ("serious", "critical")]
    if any(c["fails"] for c in results["contrast"]):
        bad.append("color-contrast (hand-measured)")
    print(f"\nserious/critical axe rules: {bad or 'none'}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
