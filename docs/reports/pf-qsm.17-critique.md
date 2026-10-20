# pf-qsm.17 — Critique of the whole portfolio

Date: 20.10.2026. Method: `/impeccable critique`. I looked at the screenshots myself (assessment A). A separate sub-agent ran the detector and the browser checks (assessment B). It worked apart from me. Its report arrived while I was still on the exhibition rooms, so the exhibition findings are not fully blind to it. I changed no site files.

Screenshots: `tests/out/pf-qsm.17/<page>-<theme>-<width>-<n>.png` (n = 0 is the top of the page, 1–4 are the next screens down, `-menu` means the phone menu is open). Detector screenshots: `tests/out/pf-qsm.17/detector/`.

## Verdict

The site is clean, calm and technically sound. It has no console errors, no broken images, no sideways scroll and alt text on every image. The near-black / off-white homepage and the plum L'Boulevard exhibition both look designed, not like templates. But the homepage does not yet do what the brief asks. The brief wants a full-width cinematic first screen, and the home is a 760 px photo in a column with empty space beside it. Nothing below the hero leads into Photography, Design or the best projects. Your strongest work, L'Boulevard, is not visible until someone finds a small menu entry. Inside the photo projects, the grid crops every picture to the same 4:5 or 16:9 box. This cuts heads and turns wide photos into tall ones, which is the worst problem for a photographer's site. The exhibition is the best part of the site: its curation, mats and captions are strong. It sits in its own visual world, and on a phone the frame puts a lot of chrome on top of it. Fix the crops and the home first. Most other problems are small copy and consistency fixes.

Score (Nielsen, 8 of 10 apply to a portfolio): **22 / 32, "acceptable", close to "good"**. Weakest: consistency (2) and minimal design (2).

## Problems, most important first

### 1. The photo grid cuts the photos badly — **medium**
- Page: every photo project. Worst on `#photography/jazz` and `#workshops/poster-making`. Both themes, both widths.
- Screenshots: `jazz-dark-1440-0.png`, `jazz-dark-1440-1.png`, `workshop-dark-1440-0.png`, `workshop-light-390-1.png`
- What is wrong: Every image is forced into a 4:5 box, and the 4th image is always forced into a 16:9 box, whatever shape the photo really has. In Jazz the 4th photo is a tall portrait of the bass player, cut into a wide strip through his forehead. All 16 workshop photos are landscape but are shown as tall portraits, so people at the tables are cut off.
- Fix: Show each photo in its own shape: drop the forced `aspect-ratio`, or choose 4:5 / 3:2 from the real width and height. Make an image "wide" only when it is a landscape photo. The same rule applies to Technopark, Summer Sessions, Ayoub Hattab and Noches, which also mix shapes.

### 2. The homepage does not meet the brief — **big**
- Page: home (`#`), both themes, 1440 and 390.
- Screenshots: `home-dark-1440-0.png`, `home-light-1440-0.png`, `home-dark-390-0.png`
- What is wrong: The brief asks for a full-width, immersive hero with the text on the photo. Under it, it asks for three entry points (Photography strongest, then Design, then Selected projects). Now the hero is a 760 px photo with text under it. About 360 px on the right is empty at 1440, and the bottom third of the phone screen is empty. "EXPLORE MY WORK →" opens one club night (Summer Sessions), not the work.
- Fix: Make the hero photo fill the main area (edge to edge, about 85–100 svh), with the label, headline and CTA set on the image's darker part. Below it, add three image entry points with real photos: Photography (large), Design (posters), L'Boulevard. Point the CTA at the Photography entry or the first section of that list.

### 3. A "Placeholder" note is shown to visitors on About — **small**
- Page: `#about`, both themes, both widths.
- Screenshots: `about-dark-1440-0.png`, `about-light-390-0.png`
- What is wrong: A dashed box says "Placeholder: your longer story goes here… Send the text and it replaces this line." This is a note to you, but every visitor sees it. The About page also has no photo of you or of your work, so it is the only page with no image on a photographer's site.
- Fix: Hide the box until the real text exists, or ask for the bio now. Add one portrait or one strong photo to the page.

### 4. L'Boulevard inside the portfolio is heavy on a phone — **medium**
- Page: `#photography/boulevard` and `#photography/boulevard/Band`, both themes, 390.
- Screenshots: `frame-light-390-0.png`, `frame-band-light-390-0.png`, `frame-dark-390-menu.png`
- What is wrong: The phone shows the SKIMART bar, then two rows of exhibition buttons ("FACES" is cut off on the right), then a theme button and Instagram buttons. That is about 190 px of controls before the first photo. The exhibition also scrolls inside its frame, so there are two scroll areas on one screen.
- Fix: On phones, open the exhibition rooms as full pages (or hide the SKIMART bar while the frame is open) so there is only one scroll. Put the exhibition nav in one row that scrolls sideways, and move the theme and Instagram buttons to the page footer.

### 5. Two theme switches that do not agree — **small**
- Page: home → `#photography/boulevard`, both themes.
- Screenshots: `home-light-1440-0.png` then `frame-dark-1440-0.png`
- What is wrong: The homepage saves its choice in `skm-theme` and the exhibition saves its own in `lbv-theme`. If you choose "light" on the homepage, the exhibition can still open dark. The homepage switch also disappears while the exhibition is open.
- Fix: Use one saved choice for both (for example, let the exhibition read `skm-theme` when it has no `lbv-theme` yet, and write both when it changes).

### 6. Your best work is hidden in the menu — **medium**
- Page: home and side menu, both themes, both widths.
- Screenshots: `home-dark-1440-0.png`, `jazz-dark-1440-0.png` (menu open)
- What is wrong: L'Boulevard is the most finished and most personal work, and the brief names Connection, Faces and Eyes as the first projects to show. But you only reach it through Photography → the 4th line → a small 9 px "exhibition" tag. No L'Boulevard photo appears anywhere on the home.
- Fix: Give L'Boulevard one of the entry points under the hero (see #2), with one matted print and the line "Exhibition · 3 rooms". In the menu, put it first in Photography.

### 7. Every project page looks the same — **medium**
- Page: all `#photography/*` and `#workshops/*` pages, both themes.
- Screenshots: `jazz-dark-1440-0.png`, `workshop-dark-1440-0.png`, `personal-light-1440-0.png`
- What is wrong: Each project is a title, a grey info line, "click any photo to enlarge", then the same 3-column grid. Nothing tells you which photo is the best one. A 4-photo night and a 19-photo night look the same, unlike the exhibition, where the order tells a story.
- Fix: Open each project with its strongest photo, large (one per project, you choose; no new text needed). Then show the rest in the grid. For projects with 4 photos, use 2 large columns, not 3 small ones.

### 8. The side menu is hard to read — **medium**
- Page: side menu, both themes, 1440 and 390.
- Screenshots: `jazz-dark-1440-0.png`, `home-dark-390-menu.png`, `frame-dark-1440-0.png`
- What is wrong:
  - The numbers mean different things. "PHOTOGRAPHY 4" counts groups, "american arts center 6" counts projects, and none of them counts photos.
  - Section names are in CAPS but project names are in lowercase. This turns names into "jamila & the other heroes" and "noches de ramadán", and the long ones wrap onto two lines.
  - The "EXHIBITION" tag touches the right edge.
  - The "PHOTOGRAPHER / VISUAL ARTIST" tagline breaks into "VISUAL / ARTIST".
  - On the phone, the menu pushes the page down instead of covering it, and the button still says "MENU" when the menu is open.
- Fix:
  - Remove the counts, or show photo counts only.
  - Write project names as they are really spelled (Jamila & the Other Heroes).
  - Widen the sidebar to about 280 px, or shorten the tagline to "Photographer".
  - Make the phone menu cover the page, and change its label to "CLOSE" when it is open.

### 9. The names and words do not match between pages — **small**
- Page: home, About, exhibition rooms, both themes.
- Screenshots: `home-dark-1440-0.png`, `frame-band-dark-1440-0.png`, `movement-dark-1440-0.png`, `hub-light-1440-1.png`
- What is wrong:
  - Your name is "Mohamed Ghoujlami" on the home but "Ghoujlami Mohamed" in every exhibition room.
  - The brand is "SKIMART", "Skimart" and "Skimart™".
  - The venue is "American Arts Center" in Photography but "American Art Center" in Design and Workshops.
  - The footer says "Shoot & designed by" instead of "Shot & designed by".
  - "Matted in #EEFFE5" puts a colour code in front of visitors.
  - "Photographer / Visual Artist" appears 3 times on the home screen (sidebar, label, page title).
- Fix:
  - Choose one name order and one brand spelling and use them everywhere.
  - Use the venue's real name everywhere.
  - Fix "Shot", and change the colour code to "cream mat" or remove it.
  - Keep the descriptor in one place only on the home.

### 10. In the light theme, dark photos lose their mat — **small**
- Page: exhibition rooms and hub, light theme, both widths.
- Screenshots: `band-light-1440-2.png`, `faces-light-1440-2.png`, `movement-light-390-1.png`
- What is wrong: In light mode the cream mat is painted plum. These photos are mostly dark plum too, so the edge of the photo disappears into the mat ("Into the light", "Chin up"). The prints read as dark slabs, not as matted prints. The project rule also says the prints have a cream `#EEFFE5` mat.
- Fix: Keep the cream mat in both themes and add a thin plum line or a soft shadow around it so it stands out on the cream wall. The "closer look" viewer already does this.

### 11. Some small text is too faint — **small**
- Page: home, project pages, side menu, exhibition titles. Both themes.
- Screenshots: `home-light-1440-0.png` ("CASABLANCA, MOROCCO"), `jazz-light-390-0.png` ("click any photo to enlarge"), `hub-light-1440-1.png` (blue subtitle)
- What is wrong: These measure under 4.5:1 contrast:
  - "CASABLANCA, MOROCCO", the "click any photo" hint and the menu counts: 2.9:1.
  - The 9 px "EXHIBITION" tag: 3.2:1.
  - The blue exhibition subtitles ("Metal Day · Casablanca", "The stage and audience") on a phone in light mode: 3.7:1, because they use `--blue` instead of `--blue-text`.
- Fix: Use `--mute` (not `--dim`) for those labels, make the tag at least 10 px, and use `--blue-text` for `.name .sub`.

### 12. Touch targets on the phone are small — **small**
- Page: home, About, all pages with the top bar. 390, both themes.
- Screenshots: `home-dark-390-0.png`, `about-light-390-0.png`
- What is wrong: These are smaller than the 44 px a finger needs:
  - "MENU" is 47 × 19 px.
  - The SKIMART logo is 28 px tall.
  - "EXPLORE MY WORK →" is 25 px tall.
  - The email and Instagram links on About are 17 px tall.
  
  The exhibition pages already fix this for touch screens.
- Fix: Add padding so each of these is at least 44 px tall, the same way the exhibition's `pointer: coarse` rule does it.

### 13. Decorations that promise something they do not do — **small**
- Page: Movement, Connection, Faces, both themes, both widths.
- Screenshots: `movement-dark-1440-1.png`, `faces-dark-1440-1.png`
- What is wrong: Every section has a QR code that does not scan (the code says "decoration only, not scannable"). A phone visitor will try it and get nothing. The QR code, the blue "XXXX", "SECTION I", the side counter and the glow on the titles all appear together, and they pull the eye away from the prints.
- Fix: Remove the QR codes, or make them real and point them at the room's link. Keep at most two of the other marks per section.

### 14. The "click any photo to enlarge" line on every project — **small**
- Page: all project pages, both themes. Strongest on 390.
- Screenshots: `jazz-light-390-0.png`, `personal-dark-390-1.png`
- What is wrong: The same hint is printed on every project. On a phone the "⤢" icon also sits on every photo all the time, and "click" is the wrong word for touch.
- Fix: Remove the hint line. The zoom cursor and the icon on hover are enough on desktop. On phones, show the icon only on the first photo, or not at all.

## What already works — keep it

1. **The exhibition's curation and labels.** Each room is ordered by an idea (shutter speed in Movement, the time of night in Connection). The cream mats and the short title + EXIF caption under each print feel like a real exhibition. This is the most "authored" part of the site.
2. **The portfolio wears the exhibition's colours when L'Boulevard is open.** The sidebar turns plum and follows its light/dark switch, so the step into the exhibition feels planned, not like leaving the site.
3. **The quiet homepage type and palette.** Archivo + IBM Plex Mono on near-black / warm off-white, thin rules, no cards, gradients or rounded corners. This matches the brief's "editorial, minimal" and keeps the photos in front.
4. **The poster pages never crop a poster** (`object-fit: contain` on the card colour), and the photo viewer is good: arrow keys, Esc, swipe, and click-to-zoom.
5. **The technical base is clean.** No console errors, no failed requests, no sideways scroll, alt text on every image, and no blurry upscaled images at 390 or 1440 (checked by the detector sub-agent).

## Detector notes (assessment B, short)

- 180 detector hits in 5 files. Most are false positives: "low contrast" measured against white instead of the real plum or cream wall, and "broken image" on the empty viewer `<img>`.
- The real ones are already in the list above: the blue `.name .sub` contrast (#11), the glow and the stripe effects (#13), and the 11 px label size (deliberate).
- I did not check hover-state contrast, the keyboard path, or the inside of the opened viewer.
