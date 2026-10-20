# pf-qsm.4 — Accessibility audit (axe-core, both themes)

Run: `~/.venvs/playwright/bin/python -I tests/pf-qsm.4_a11y.py [base-url]` (default http://localhost:8027/, about 4 minutes, exits 1 today). axe 4.10.2 on 14 views (including open viewers and the exhibition iframe), light and dark, at 390 and 1440 px. Contrast, Tab focus, the viewer focus trap, alt texts, headings, title/lang and tap targets are also checked by hand. Output: `tests/out/pf-qsm.4/` (gitignored).

Note: the agent's last script change (hand contrast check extended to the homepage) was not re-run. The homepage contrast numbers come from a one-off run of the same code.

## Verdict
Not WCAG 2.1 AA yet. There are 4 serious problems, each a small CSS or JS fix. The exhibition pages are close to passing; most problems are on the homepage (`index.html`).

## Serious
1. **Homepage photo viewer lets focus escape.** It says `aria-modal`, but after 2 Tabs focus moves to the page behind it (body, logo, about, menu…). This happens in every view with the viewer, in both themes.
   Fix: in `openLb` set `document.getElementById('side').inert = view.inert = true`, and back to false in `closeLb`. The exhibition viewers already do this and pass.
2. **Hidden menu links still take keyboard focus.** Links inside closed menu sections (`.list` 0fr rows, overflow hidden) stay in the Tab order. On home at 1440, 18 of 28 Tab stops are invisible; on project views it is 8 to 17. (WCAG 2.4.7, 2.4.3)
   Fix: `.list>div{visibility:hidden;transition:visibility .3s}` and `.open>.list>div{visibility:visible}`.
3. **Some text has too little contrast** (WCAG asks 4.5:1 for small text).
   - Homepage `--dim` text: `.loc`, `.hint`, menu counts `.n`, viewer counter `#lb-c` = 2.78–2.95:1 in both themes. In exhibition mode the menu counts are 2.85:1 (light) and 3.9:1 (dark).
     Fix: `--dim` `#7d7a75` in dark (4.63:1) and `#6f6c67` in light (4.56:1), the same in `.lb`. Raise the `--dim` alpha in `body.lbv-on`, then re-check.
   - Homepage "exhibition" tag `.ex` in light: `#3d81ff` on `#f2efe9` = 3.16:1 at 9 px. Fix: `#1f5fd6` in light (4.99:1).
   - Exhibition subtitle `.sub` on the hub and all rooms at 390: `#337aff` = 3.74:1 light, 4.37:1 dark (passes at 1440 because the text is large). Fix: `color: var(--blue-text)` (4.7:1 dark, 5.47:1 light).
   - axe can't measure exhibition text contrast because the grain `::after` layer covers it, so it was measured by hand. Apart from `.sub`, all exhibition text passes.
4. **Faces Instagram handles (`.who`) look like plain text except for colour** (19 links, both themes; WCAG 1.4.1). Fix: `.who{text-decoration:underline}`.

## Moderate
5. **Homepage alt texts say nothing** ("Jazz, photo 3"). Also, the figure's `aria-label="Enlarge photo 3"` hides the alt, so a screen reader says "Enlarge photo 3, button". Fix: a short description per image in `WORK`; drop the aria-label or make it "Enlarge: <alt>". The exhibition alts are good. (→ pf-qsm.25)
6. **No h1** on homepage project pages, About or the exhibition view; the title is an h2 (axe, 20 runs). Fix: render `.proj` headings as h1 with the same style.
7. **`document.title` never changes** between homepage views. Fix: in `render()`, `document.title = (project name or 'About') + ' — SKIMART'`. (→ pf-qsm.21)
8. **Small tap targets at 390:** MENU 47×19, logo 28 px tall, CTA 25 px tall, viewer close 40×40, Faces handles 58×20 (33 targets under 24 px). 44 px is recommended. Not required by 2.1 AA, and axe's 2.2 `target-size` passes thanks to spacing. Fix: burger `min-height:44px`, `.lb .x` 44×44, `.who{display:inline-block;padding:12px 0}`.
9. **At 820 px and below, the homepage viewer hides Previous/Next**, so the only way on is to swipe; screen reader users on phones can't move to the next photo. Fix: keep the buttons, smaller.

## Minor
10. On Movement and Faces, the hero caption h2 comes before the h1 in the code. Fix: make those captions plain text.
11. Homepage focus ring is 1 px: visible but thin. Fix: 2 px, like the exhibition.
12. Desktop homepage about/contact/instagram/theme links are about 20 px tall.

## What passes
- `lang="en"` on every page.
- Each exhibition page has its own title, and the iframe has a title.
- The exhibition viewers keep focus inside and return it on Escape.
- Every visible focusable element shows a clear change on focus (checked with screenshots, method confirmed by turning outlines off).
- Exhibition alt texts describe the photos well.
- No ARIA, name, label or landmark errors in axe, and no page errors.

## Not checked
Real screen readers, the 820 px width, and tabbing with the phone menu open. The fix colours were calculated, not yet tried: run the script again after applying them.
