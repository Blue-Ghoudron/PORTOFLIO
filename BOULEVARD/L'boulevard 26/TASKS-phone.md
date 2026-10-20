# Phone pass: zoom, design, layout

Branch: `L'Boulevard-Page-Branch`. Pages: `index.html` (L'Boulevard hub), `Movement/`, `Band/` (Connection), `Faces/`.
Status (20.10.2026): done, phone pass committed on the branch (see Findings).

Goal: every page works and looks designed on a phone, in light and dark, with nothing left unchecked.

## 1. Zoom
- [x] Pinch-zoom and double-tap zoom work on every page (viewport meta, `touch-action`, no `user-scalable=no`).
- [x] Closer-look viewer on phone: photo can be pinch-zoomed; swipe (prev/next) doesn't fight the zoom; Close/Prev/Next stay reachable while zoomed.
- [x] The desktop page scale (`html { zoom: .75 }` at ≥1440px) never applies on phones or tablets, and nothing relies on it below 1440px.
- [x] Text doesn't auto-inflate or shrink in landscape (`text-size-adjust`).
- [x] Rotating portrait ↔ landscape keeps the layout (svh sizes, hero, viewer).

## 2. Layout (320, 360, 375, 390, 414, 430 portrait; 844×390 landscape; 768, 820 tablet)
- [x] No content cut off or sideways scroll (`overflow-x: hidden` can hide overflow, so check each element's box against the viewport).
- [x] Top strip: 4 page buttons + theme + handles. It now takes 2–3 rows; make it compact and clean.
- [x] Hero: giant title, subtitle, prologue print, tag and label fit and don't overlap.
- [x] Rooms, room heads, QR tags, cubes, drift layout, "In motion" / "17 seconds" strips, study wall, gallery: sizes and gaps on phone.
- [x] Hub doors stack well; labels line up.
- [x] Outro ("Way out" / "Lights down"), globe and footer.
- [x] Safe areas (notch, home bar) at the edges and in the viewer.

## 3. Design and usability
- [x] Tap targets are at least 44×44 px (nav buttons are 40px tall now).
- [x] Small mono text stays readable (≥11px) and keeps its contrast in both themes.
- [x] Hover-only effects have a sensible touch equivalent; no sticky hover after a tap.
- [x] Keyboard focus and the viewer's focus trap still work.

## 4. Done means
- [x] Each item above checked with Playwright (phone emulation with touch) at the listed sizes, both themes, every page, with screenshots looked at.
- [x] Every nav link, door and the theme button clicked through (`navflow` check), plus the viewer opened, swiped and closed on phone.
- [x] Desktop (1440) looks the same as before.
- [x] Findings and fixes written below; fixes committed on the branch.

## Findings

Tested with Playwright (Chromium, touch phone emulation: iPhone 13, Pixel 7, plus 320, 360, 375, 390, 414, 430 portrait, 844×390 landscape, 768 and 820 tablet, light and dark). Scripts and screenshots: `~/.cache/lbv-phone/` (`shots.py`, `parts.py`, `viewer.py`, `rotate.py`, `heads.py`, `hover.py`, `desk.py` + `pxdiff.py`, `navflow.py`).

### Fixed
- **Viewer pinch-zoom (Movement, Connection, Faces).** The photo had `touch-action: pan-y`, so a pinch on it did nothing, and the two-finger touch was read as a tap, which moved to the next photo. Now `pan-y pinch-zoom`. A second finger or a zoomed screen is never read as a swipe or tap. While zoomed the photo pans freely, and Prev/Next/Close stay pinned at normal size to the top right of the zoomed view. Test: pinch went from scale 1.00 to 5.00, panning sideways while zoomed moved the view without changing the photo, Close could be tapped while zoomed, pinching back in returned to 1.00.
- **Top strip on phones (≤560px).** The four pages now sit in an even 2 × 2 block, with theme on the left and handles on the right of the line below, edge to edge. 390px: 155px tall on every page. Before it was 147px with ragged rows on three pages and 197px on Connection. 320px Connection: 205px, was 247px.
- **Tap targets.** Page buttons, theme, handles and route links are 44px tall on touch screens (`pointer: coarse`). Desktop keeps 40px. Faces sitter handles (`@name`) get a 44px tall hit area without moving the text.
- **Hub subtitle cut off on phones.** "Metal Day · Casablanca · 2025–2026" ran past the screen edge at 320–430, because it inherited `nowrap` from the giant name and the overflow was hidden by `overflow-x: clip`. It wraps now.
- **Room title ran under the QR code.** "Dissolving" (Movement) at 320–414 and "Painted" (Faces) at 320 overlapped the code. On phones the QR column is now only as wide as the code, with its label running left under it, and the gap is 8px below 360px.
- **Small text under 11px.** Faces subtitle "Close to the lens" was 6.8–9.4px on phones, Movement and Connection subtitles were 10–10.4px at 320: now at least 12px. QR labels ("Section I", "In motion", "17 seconds", "Study wall") were 10px below 1440: now 11px. Contrast of the small text checked: dim ink 7.7:1 dark / 5.8:1 light, small blue 4.7:1 dark / 5.5:1 light.
- **Landscape phone prologue.** On Faces at 844×390 the portrait was about 3 screens tall, and on Movement the frame was taller than the screen. Both now fit the screen height (`--svh`). Connection already did this.
- **Hub doors at 761–1439px (e.g. landscape phones).** "Faces and Eyes" wraps, which lifted that print, so the three prints and their label rules sat on different lines. They now start on one line. At 1440 nothing changes.
- **Sticky hover after a tap.** The blue mat ring, corners and filter on a tapped print, the blue Prev/Next after a tap, and the theme button border stayed lit until the next tap. Hover looks now apply only where hover exists, and the press feedback (`:active`) stays.
- **iOS text inflation in landscape:** `text-size-adjust: 100%`.
- **Safe areas.** `viewport-fit=cover` added to the viewport meta, so the existing `env(safe-area-inset-*)` padding (page gutters, viewer) works on notched iPhones. Before it was always 0.

### Checked, no change needed
- Viewport meta allows zoom (no `user-scalable=no`, no `maximum-scale`). Page pinch-zoom works, and nothing on the page sets `touch-action` apart from the viewer photo.
- `html { zoom: .75 }` applies only at ≥1440px. Computed zoom is 1 at every phone and tablet size, and nothing below 1440 depends on it.
- Rotating portrait ↔ landscape, both on the page and with the viewer open: nothing leaves the screen, the photo fits, and the caption still starts at the photo's edge.
- No element box past the screen edge at any listed size. The only ones are the skewed grid panel behind Connection's prologue, which is decorative and clipped by `.wrap`, and the film and contact strips, which scroll by design.
- Keyboard: Enter opens the viewer, Tab cycles Prev → Next → Close → Prev, Esc closes and focus returns to the print.
- Desktop 1440×900, full page, light and dark, all four pages: pixel-identical before and after.
- `navflow.py`: "all nav links + theme button work" (http and file://, 390/820/1440, both themes). `qa_check.py` (390, 820, 1440, 844×390, 320; light and dark; links): no issues on all four pages.

### Not verifiable here
- Real iOS Safari pinch and visual-viewport behaviour can't be fully emulated. Chromium pinch was driven with raw two-finger CDP touches. On an iPhone, check that the pinned buttons follow the zoomed view smoothly. Notch and home-bar insets can't be emulated either.
- Double-tap zoom on the viewer photo is off on purpose. A single tap on either half already means prev/next, and `pinch-zoom` without `manipulation` turns off double-tap zoom. Everywhere else on the page double-tap zoom is left to the browser.

### Proposals for the owner (taste, not done)
- **Top strip:** a one-line alternative for phones is the four pages as a single row that scrolls sideways, with theme and handles moved to the footer. That would take about 50px instead of 155px but hides "Faces and Eyes" off-screen at first. A small "Pages" menu is another option. At 320px the two Connection handles still take two lines.
- **Hero order on phones:** Movement and Faces show the prologue print first and the name under it, while Connection shows the name first. Pick one order for all three.
- **Landscape giant titles:** "MOVEMENT" and "CONNECTION" fill the width at 844×390 and take about half the screen height. They could be capped by `svh` in landscape if that feels too loud.
- **Light-theme viewer:** the cream viewer background hides the cream mat, so the print floats without its border. A slightly darker viewer wall in light (e.g. `--wall-2`) would show the mat.
- **Faces landscape prologue caption** wraps to three lines under the narrower portrait ("· ISO / 6400"). The caption could sit beside the print in landscape.
- The giant titles go 2–10px past their column into the side gutter on phones (Anton glyph overhang, never off-screen). The divisors (4.05 / 4.42 / 5.95) could be nudged if exact edge alignment matters.
