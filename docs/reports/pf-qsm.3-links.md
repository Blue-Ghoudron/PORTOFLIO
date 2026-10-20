# pf-qsm.3: links, images, console and network

**Verdict: PASS. Nothing is broken.** All images load, all links work, and there are no JS errors and no failed requests. Two small clean-up items (not bugs) are at the end.

- Date: 2026-10-20, site at http://localhost:8027/
- Run: `~/.venvs/playwright/bin/python -I tests/pf-qsm.3_links.py [base-url]` (default `http://localhost:8027/`, exit code 1 on any error, about 90 s)
- Screenshot: `tests/out/pf-qsm.3/home_fonts-blocked_1440.png`. The script saves more screenshots only for views that fail.

## What was checked

24 views, each at 390x844 and 1440x900:

- Homepage: `#` (home), `#about`, all 14 `#<section>/<project>` routes from the WORK array, and `#photography/boulevard` with `/Movement`, `/Band`, `/Faces` (and the images inside the iframe).
- The 4 exhibition pages on their own: hub, Movement, Band, Faces.

On each view the script scrolls to the bottom, so lazy images load. It also slides each sideways strip to its end. Then it checks:

1. **Images**: every `<img>` with a `src` has `naturalWidth > 0`. CSS background images (the film grain `grain.jpg`) return 200. Result: **all OK.**
2. **Links**: every `a[href]` and `link[href]`. Same-site links must return 200. For `#id` links on exhibition pages, the element must exist. Homepage `#...` links must be real routes. `mailto:` must be well formed. Result: **all OK.** One mailto: `ghoujlamimohamed@gmail.com` (correct).
3. **Console and network**: no `pageerror`, no `console.error`, no 4xx/5xx and no failed request. Result: **all clean**, at both widths.
4. **Google Fonts blocked** (requests to `fonts.googleapis.com` and `fonts.gstatic.com` are aborted): the home page renders with the fallback font (system-ui). The headline, text, menu and photo are all there. No web font is loaded, and there are no JS errors. The only console messages are the blocked font requests, which is expected. See the screenshot.
5. **WORK images**: all 132 image ids in the WORK array have a file in `assets/home/`. None is missing.

External links: all 26 Instagram links answer 200 (instagram.com, the profile itself is not verified). The two Google Fonts stylesheets answer 200. `https://fonts.googleapis.com/` answers 404, but that is only the `<link rel="preconnect">` target, not a link people click. This is normal.

## Note on the first run

The first run said that 4 images did not load at 390 px: `Movement/images/mov-26-0160.jpg`, `mov-26-0165.jpg`, `Faces/images/fac-26-0547.jpg`, `fac-26-0548.jpg`. This was **not a bug**. At 390 px these photos sit in a sideways film strip (`div.film`), off screen to the right. They use `loading="lazy"`, so the browser loads them only when you swipe the strip. When the strip is swiped they load fine (checked). The script now swipes the strips too.

## Clean-up items (not bugs)

1. **3 unused files in `assets/home/`**: `b-con.jpg`, `b-fac.jpg`, `b-mov.jpg` (about 400 KB together). Nothing in the site uses them. They were the door photos of the old Boulevard overview. Since commit `79bb8ec` the exhibition opens in an iframe, so they are no longer used. All the other 133 files are used (132 in WORK, plus `s23.jpg` for the home photo).
   *Smallest fix:* delete the 3 files.
2. **Dead data in WORK**: the `boulevard` project still has `doors:[['Connection','Band'],...]`. `render()` never reads it anymore.
   *Smallest fix:* remove the `doors:` line from the WORK entry in `index.html` (together with item 1).
