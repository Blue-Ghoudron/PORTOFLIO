# pf-qsm.13 — Content check: placeholders, titles, share previews

Date: 20.10.2026 · Checked: `index.html` (home, about, 14 project views) and the 5 exhibition pages (hub, Movement, Connection, Faces and Eyes), source and rendered at http://localhost:8027/.
Helper: `tests/pf-qsm.13_content.py` → `tests/out/pf-qsm.13/content.json`. Nothing on the site was changed.

## Verdict

**Not ready to share yet.** The text is mostly clean and short, but:

- No page has share tags or an icon. A link sent on WhatsApp or in an Instagram DM shows only a bare address, with no photo and no title.
- Three unfinished texts can be seen on the site: the About placeholder, and "Layout draft" in two exhibition footers.
- The same place has two names: "American Arts Center" and "American Art Center".
- Some facts are said twice (Movement, Home/About), and one fact is wrong (the f-numbers in the Faces text).

All fixes are small. They are listed below, most important first.

What is already fine:
- `lang="en"` is on every page.
- All dates use dd.mm.yyyy.
- "L'Boulevard" has the same spelling everywhere a visitor can see it.
- All 70 exhibition photos have real, descriptive alt text.
- No image is missing its alt.

---

## Findings

### 1. No share preview on any page (no description, no Open Graph, no Twitter tags)
**Where:** all 5 HTML files. `index.html` has only `<title>`; the 4 exhibition pages also have only `<title>`.
**What:** there is no `meta description`, `og:title`, `og:description`, `og:image`, `og:url` or `twitter:card` anywhere. WhatsApp, Instagram DMs, Facebook and iMessage show a picture and a title only when these tags exist.
**Notes:**
- `og:image` and `og:url` must be **full addresses** (`https://…`). The site is not published yet, so `SITE` below stands for the real address. Replace it when the site is published.
- Everything after `#` is ignored by WhatsApp and the other preview readers. Every homepage view (`#photography/jazz`, `#about`, …) shares the homepage preview. Only the 5 real HTML files can have their own preview.
- All texts below are copied from the site. The images are existing photos, landscape, under 310 KB (WhatsApp skips large images).

**Fix: add in `<head>`, after `<title>`:**

`index.html`
```html
<meta name="description" content="I'm Mohamed Ghoujlami, aka SKIMART. I capture people, places and culture through photography, design and visual storytelling.">
<meta property="og:type" content="website">
<meta property="og:site_name" content="SKIMART">
<meta property="og:title" content="SKIMART — Photographer / Visual Artist">
<meta property="og:description" content="Real moments. Visual stories. Casablanca, Morocco.">
<meta property="og:image" content="https://SITE/assets/home/s23.jpg">
<meta property="og:image:width" content="1600"><meta property="og:image:height" content="1067">
<meta property="og:image:alt" content="Man in round sunglasses and a Space Invaders jacket under purple club light">
<meta property="og:url" content="https://SITE/">
<meta name="twitter:card" content="summary_large_image">
```

`BOULEVARD/L'boulevard 26/index.html` (hub)
```html
<meta name="description" content="Two Metal Days, three rooms: the crowd in motion, the stage and the people looking back at it, and the faces between sets.">
<meta property="og:type" content="website">
<meta property="og:site_name" content="SKIMART">
<meta property="og:title" content="L'Boulevard — Metal Day · Casablanca · 2025–2026">
<meta property="og:description" content="Two Metal Days, three rooms: the crowd in motion, the stage and the people looking back at it, and the faces between sets.">
<meta property="og:image" content="https://SITE/BOULEVARD/L'boulevard%2026/Band/images/frame-01.jpg">
<meta property="og:image:alt" content="A giant projected eye on the left screen, the singer raising a fist at centre stage">
<meta property="og:url" content="https://SITE/BOULEVARD/L'boulevard%2026/">
<meta name="twitter:card" content="summary_large_image">
```

`Movement/index.html`
```html
<meta name="description" content="The pit has its own show, played with its back to the stage. Photographs from two Metal Days at L'Boulevard, hung by shutter speed.">
<meta property="og:title" content="Movement — L'Boulevard · SKIMART">
<meta property="og:description" content="Away from the stage. Metal Day, L'Boulevard · Casablanca · 2025–2026">
<meta property="og:image" content="https://SITE/BOULEVARD/L'boulevard%2026/Movement/images/mov-25-9206.jpg">
<meta property="og:image:alt" content="A whole crowd blurred into motion in front of a bright stage">
<meta property="og:url" content="https://SITE/BOULEVARD/L'boulevard%2026/Movement/">
<meta property="og:type" content="website"><meta property="og:site_name" content="SKIMART"><meta name="twitter:card" content="summary_large_image">
```

`Band/index.html` (Connection)
```html
<meta name="description" content="A stage only works when someone looks back. Photographs from two Metal Days at L'Boulevard: the floor, the stage, the look.">
<meta property="og:title" content="Connection — L'Boulevard · SKIMART">
<meta property="og:description" content="The stage and audience. Metal Day, L'Boulevard · Casablanca · 2025–2026">
<meta property="og:image" content="https://SITE/BOULEVARD/L'boulevard%2026/Band/images/frame-07.jpg">
<meta property="og:image:alt" content="Light beams fanning out over the drum riser, the band small against the glowing backdrop">
<meta property="og:url" content="https://SITE/BOULEVARD/L'boulevard%2026/Band/">
<meta property="og:type" content="website"><meta property="og:site_name" content="SKIMART"><meta name="twitter:card" content="summary_large_image">
```

`Faces/index.html`
```html
<meta name="description" content="Between sets the camera turned around. Faces from two Metal Days at L'Boulevard, Casablanca.">
<meta property="og:title" content="Faces and Eyes — L'Boulevard · SKIMART">
<meta property="og:description" content="Close to the lens. Metal Day, L'Boulevard · Casablanca · 2025–2026">
<meta property="og:image" content="https://SITE/BOULEVARD/L'boulevard%2026/Faces/images/fac-26-0545.jpg">
<meta property="og:image:alt" content="The same face in spiked glasses, wider, the crowd around her">
<meta property="og:url" content="https://SITE/BOULEVARD/L'boulevard%2026/Faces/">
<meta property="og:type" content="website"><meta property="og:site_name" content="SKIMART"><meta name="twitter:card" content="summary_large_image">
```
(The Faces portraits are tall and 1 MB. `fac-26-0545` is landscape and 309 KB, so it works for previews. It shows a tagged person (@rasha_wt). If you prefer a photo with no tagged person, choose another one.)

### 2. No favicon and no apple-touch-icon
**Where:** all 5 pages. There is no icon file in the repo, and the browser asks for `/favicon.ico` and gets 404.
**What:** the browser tab and a phone home-screen shortcut show a blank or default icon.
**Fix:** make one icon from the SKIMART oval logo that is already in every exhibition footer (`<svg class="brand">`). Save it as `favicon.svg` in the repo root, plus a 180×180 `apple-touch-icon.png`. Then add:
```html
<!-- index.html -->
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<!-- hub: href="../../favicon.svg" and "../../apple-touch-icon.png"; rooms: "../../../favicon.svg" and "../../../apple-touch-icon.png" -->
```

### 3. About: placeholder text can be seen (known)
**Where:** `index.html` line 227, view `#about`.
**What:** "Placeholder: your longer story goes here (how you started, what you look for in a picture). Send the text and it replaces this line."
**Fix:** replace it with the user's bio when it arrives. Until then, delete the line (the About view still works without it). Do not publish with it.

### 4. "Layout draft" and work notes in the exhibition footers
**Where:**
- `Movement/index.html` footer: "10 works hung, 4 frames in motion · 1882 px wide · **Layout draft**"
- `Faces/index.html` footer: "10 works hung, 4 frames in sequence, 22 in the gallery · 1882 px wide · **Layout draft**"
- `Band/index.html` footer: "13 works hung, 4 on the study wall · 1882\*1282 / 1282\*1882 px"

**What:** "Layout draft" tells visitors the page is unfinished. The pixel sizes are notes for you, not for visitors. The three footers also say the same thing in three different ways.
**Fix:** delete "· Layout draft" (2 places). Optional: also delete "· 1882 px wide" and "· 1882\*1282 / 1282\*1882 px". The counts can stay.
(Also only for you, and less visible: "Matted in #EEFFE5." in the three credit lines. A visitor does not read a colour code. Keep it only if you like it as a detail.)

### 5. "American Arts Center" vs "American Art Center"
**Where:**
- "American **Arts** Center": `index.html` lines 173–178. That is the menu group and the info line of Ayoub Hattab, Jamila, Jazz, Nanofunk, Disco Atlas and Noches de Ramadán (7 times). The spec also says "Arts".
- "American **Art** Center": line 183, Design › project title "American Art Center", and line 189, Workshops › Poster Making info "American Art Center · 13.02.2026" (2 times).

**Fix:** use one name everywhere. Most of the site and the spec say "American Arts Center", so change lines 183 and 189 to that. Ask the user to confirm the official name.

### 6. Movement: the intro says each shutter fact, then each room says it again
**Where:** `Movement/index.html`, intro and room headers.
- Intro: "…at 1/5 s and 1/13 s people turn into movement, at 1/60 s they still smear, and at 1/250 s the crowd holds still."
- Room I: "From 1/13 s to 1/30 s, faces and bodies **turn into movement**."
- Room II: "At 1/50 s and 1/60 s the bodies **still smear**."
- Room III: "At 1/250 s **the crowd holds still**: the pit opening, an embrace, arms up."

The route menu and the side markers also show 1/13, 1/60 and 1/250. So each fact is said 3 times on one page. The intro and Room I also disagree: the intro says "1/5 s and 1/13 s", but Room I is 1/13 to 1/30 (1/5 s is only the prologue photo).
**Fix (cut from the intro only):**
> "The pit has its own show, played with its back to the stage. These photographs from two Metal Days are hung by shutter speed, slowest first. The slower the shutter, the closer the picture gets to how the pit feels. — Skimart"

### 7. Faces: "wide open at f/1.4 to f/2.2" is not true for all photos
**Where:** `Faces/index.html`, intro: "…taken a step away, wide open at f/1.4 to f/2.2, in light meant for the stage."
**What:** the page's own camera data says otherwise. 02 "Sign of the horns" is **f/4.5**, G01 is **f/3.5**, and G02 is **f/5**.
**Fix:** "…taken a step away, **mostly** wide open, in light meant for the stage." Or keep the numbers and add "mostly": "mostly wide open at f/1.4 to f/2.2".

### 8. Typo: "Shoot & designed by Skimart"
**Where:** footer of all 4 exhibition pages.
**Fix:** "**Shot** & designed by Skimart".

### 9. The name is written in different ways
**Where:**
- "**Mohamed Ghoujlami**": homepage hero and About ("I'm Mohamed Ghoujlami, aka SKIMART"), and the brief.
- "**Ghoujlami Mohamed**": the byline "Photographs by Ghoujlami Mohamed" on Movement, Connection and Faces.
- "**Mohamed**" only: all 4 exhibition footers, "Skimart™ is a trademark of Mohamed".
- "**SKIMART**" on the homepage (logo, text, title). "**Skimart**" in the exhibition ("— Skimart", "Shoot & designed by Skimart", "Skimart™", `aria-label="Skimart"`).

**Fix:** the user picks one order (first name first, "Mohamed Ghoujlami", matches the homepage text) and one spelling of the brand. Then use them on all pages: change the 3 bylines and the footer line. The SVG logo text is already "SKIMART".

### 10. The same words twice on one screen: Home and About
**Where:** `index.html`.
- Home view, desktop: the side menu shows "PHOTOGRAPHER / VISUAL ARTIST" under the logo, and the main column shows "PHOTOGRAPHER / VISUAL ARTIST" again. The two are side by side.
- About view: the side menu tagline again, plus the info line "Photographer / Visual Artist · Casablanca, Morocco".
- About's first paragraph is word for word the Home paragraph: "I'm Mohamed Ghoujlami, aka SKIMART. I capture people, places and culture through photography, design and visual storytelling."
- About list: "Photography — Live music, portraits, street **photography**, cultural documentation".

**Fix (small):**
- About info line → "Casablanca, Morocco".
- About list → "Live music, portraits, street, cultural documentation".
- When the real bio arrives (finding 3), let it replace the copied Home paragraph.
- On the Home view, either hide the side-menu tagline or drop the `.lbl` line. The brief asks for the descriptor in the hero, so hiding the side tagline on Home is the safer choice. The user decides.

### 11. Tab titles do not say whose site it is; the homepage title never changes
**Where:**
- Exhibition `<title>`s are only "Movement", "Connection", "Faces and Eyes" and "L'Boulevard".
- The homepage title stays "SKIMART — Photographer / Visual Artist" on every view (About, Jazz, Posters…).

**Fix:**
- Titles: "Movement — L'Boulevard · SKIMART", "Connection — L'Boulevard · SKIMART", "Faces and Eyes — L'Boulevard · SKIMART", "L'Boulevard — Metal Day · SKIMART".
- Homepage: in `render()`, set `document.title` to "`<project name>` — SKIMART" (or "About — SKIMART"), and back to the default on Home. This is one line. It helps tabs, history and bookmarks. It does not help share previews (see finding 1).

### 12. Venue written two ways
**Where:**
- "Metal Day, L'Boulevard · **R.U.C**, Casablanca": Movement and Faces bylines.
- "Metal Day, L'Boulevard · **Stade R.U.C**, Casablanca": Connection byline.

**Fix:** the same text on all three. Ask the user which one is correct.

### 13. Generic alt text on the homepage: 132 images
**Where:** `index.html` line 253. Every grid image gets `alt="<project name>, photo N"` or `"…, poster N"`.

| View | Generic alts |
|---|---|
| Technopark · Sidi Maarouf | 9 |
| Mehdi Ainak & Hellboy | 7 |
| Summer Sessions | 17 |
| Ayoub Hattab | 6 |
| Jamila & the Other Heroes | 7 |
| Jazz | 19 |
| Nanofunk | 4 |
| Disco Atlas | 4 |
| Noches de Ramadán | 4 |
| Design › American Art Center | 7 |
| Design › Personal project | 29 |
| Design › Event & music posters | 1 |
| Design › Fan poster | 2 |
| Workshops › Poster Making | 16 |
| **Total** | **132** (0 missing) |

The buttons around the images are also generic: "Enlarge photo 3".
The home hero image and all 70 exhibition images have good descriptive alts.
**Fix:** add an optional `alts:[…]` list to each project in `WORK`, and use `p.alts?.[i] || <current text>`. Fill it from someone who has looked at each photo (not from this report: the photos were not described here). Start with the CTA target, Summer Sessions, and with Jazz (the largest).

### 14. Handles and names in the project info lines
**Where:** `index.html` lines 171–172.
- "lapero.marrokii · 27.06.2025" and "liquid.bridge · Seamens Club Casablanca · 22.08.2026". These look like Instagram handles, but have no "@". In the exhibition, handles are written with "@" (e.g. "@w8yolo").
- "**Seamens** Club": please check the spelling ("Seamen's Club"?). It was not checked here.

**Fix:** write the handles with "@" (or link them, as in Faces). Confirm "lapero.marrokii" and the club name with the user.

### 15. Connection: small contradictions in the intro
**Where:** `Band/index.html`.
- The intro says the photos are "hung by what they show, **not by the clock**". But the route menu shows clock times: "I The floor 20:53 · II The stage 22:51 · III The look 23:00". These times also mix two years (23:00 is from 2025, the others are from 2026).
- The intro says "**Thirteen** photographs", but the hub door says "II · **17** photographs" (13 hung + 4 on the study wall). Both are true, but a visitor sees two numbers.

**Fix:** remove the `<time>` from the three route links, or remove "not by the clock". Optional: on the hub, count only hung works, or add "+4 study" so the numbers match.

### 16. Small copy points (the user's voice; only flags)
- Faces gallery wall: "**You can hear them loud** · 2025". This is odd English. Possible fixes: "You can hear them" or "Loud". The user decides.
- Faces Room I: "Eyes on the lens: horns up, a hood, a chin raised". But photo 04 "Chin up" has the alt "eyes shut". Check that this photo belongs in "Looking back".
- Homepage poster views: the hint says "click any **photo** to enlarge" on poster pages, and says "click" on phones. Possible fix: "click any poster to enlarge" for `poster:true`. Optional: "tap" when the device has no mouse (hover:none).
- Design › Fan poster: the info line "I'm not a human" reads like a sentence, not a label. If it is the poster's title, put it in quotes: “I'm not a human”.
- Connection subtitle "The stage and audience" (the brief has "The Stage and Audience"). This is fine as it is. "The stage and the audience" reads more naturally. Optional.
- Faces statement: "eyes" three times ("The rooms follow the eyes … and the eyes decide how much of it you get"). Optional cut: "…and they decide how much of it you get."

### 17. Leftover text that visitors do not see (clean when convenient)
- `index.html` line 179: the L'Boulevard project has `name:'Overview'`, `info:'Three rooms · each opens in its own style'` and `doors:[…]`. None of it is ever shown (the menu shows the group name; the view is the iframe). It is dead data (the spec already lists `doors`).
- `Faces/index.html`: the "14 seconds" section has `id="seventeen"`, so the address bar shows `#seventeen`. This is left over from an older name. Rename it to `id="fourteen"` and change the route link to match.
- All exhibition pages have `<meta name="claude:viewport-fit-sides" content="cover">`. This is a tool leftover with no effect in browsers. It can be deleted.
- `Band/index.html` line 444: the code comment says "(01–07)", but there are 13 works. Comment only.
- The hub CSS comments name the colours "Getfedo brand-dark / brand-light / brand-mid". These are not visible, but they show in "view source" on a SKIMART site.

### 18. Capitalisation of names (low)
**Where:** `index.html`.
- The side menu writes every project in lowercase ("mehdi ainak & hellboy", "noches de ramadán", "l'boulevard"). The page heading uses capitals. This is a style choice and it is fine.
- Inside Design and Workshops the titles mix styles: "**Poster Making**" (Title Case), but "Personal project", "Fan poster" and "Event & music posters" (sentence case).

**Fix:** "Poster making", or Title Case for all four. The user decides.

### 19. The repo name "PORTOFLIO" will show in the public address
**Where:** the GitHub remote is `Blue-Ghoudron/PORTOFLIO`. With GitHub Pages, the site address would be `…github.io/PORTOFLIO/`, and this spelling would also appear in every `og:url`.
**Fix:** before publishing, rename the repo to `PORTFOLIO` (GitHub redirects the old name), or use a custom domain. The visible site text has no "Portoflio" spelling.

---

Not checked: the photos themselves (no alt texts were written), the official spellings of venue/club/handle names, and how WhatsApp/Instagram render the previews (this needs a published address).
