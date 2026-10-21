# F.A Filter Ability — photography archive + smart filters — spec

Status: design, waiting for the user's approval. Branch `Filter-Ability` (from `Portoflio-Branch`). Beads epic `pf-coe`. Written 21.10.2026.
Source brief: `Briefs/skimart-photography-archive-brief.md` (supersedes `Briefs/Photography Archive & Smart Filtering.txt`). Its 12 acceptance criteria (§7) are the definition of done; this spec says how they are met in this repo.

## Why
Art directors, cultural organisations, event organisers and potential clients come to judge the work and find relevant photographs quickly. Today photos can only be reached project by project. They should be able to start from a genre (Music → Concert, Street → Portraits), then narrow by place, year, event or artist. It must feel like a curated photography archive, not an image database. 160 photos today, room to grow.

## Goals
- One new **Archive** view holding every photograph: the homepage photo projects (77), the three L'Boulevard rooms (67) and the Poster Making workshop (16): 160 photos. The home hero (Soualem wheat field) is not in any project and stays out (my call).
- Genre first, then metadata: what a photo is *about* (genre) stays separate from *where / when / for whom* (place, city, year, date, event, artist, client). American Arts Center is a place, never a genre.
- Filters combine; the current view lives in the address and can be shared, bookmarked and restored.
- A private **tagging page** where the user edits every field of every photo, because the user tags the genres themselves.
- Unit tests for the filter logic and Playwright tests for the UI, desktop and phone.

## Non-goals
- No backend, CMS, build step or package manager: static files on GitHub Pages (the user's decision).
- Graphic Design (Design, Workshops sections) is not filtered and not changed; it just keeps working.
- The tagging page does not add new photos or upload images; it edits records of photos that already exist.
- No Series filter in the archive (the brief makes it optional). Each photo links to its project / room instead.
- No redesign of existing project pages or L'Boulevard rooms.

## Anti-goals (a failure even if it works)
- Invented facts: genres, places, dates, events, artists, clients or descriptions that the site does not already state. Unknown stays `null` / empty.
- A generic image-database look (filter sidebars full of checkboxes, rounded cards, badges). It must read like the rest of the site.
- L'Boulevard rooms losing their design, order or identity.
- Empty or misleading filter options; a filter that silently leads to "0 photographs".
- Fixture (fake test) photos appearing on the real site.

## Decisions (the user's)
| Question | Decision |
|---|---|
| Hosting | Static on GitHub Pages, no backend |
| Which photos | All three sets: homepage photo projects, L'Boulevard rooms, Poster Making workshop |
| Genre tagging | The user tags genres themselves, later. The archive ships with genres empty |
| How to tag | A tagging page (contact sheet), not hand-editing the data file |
| Tagging page fields | Every field, not only genres |
| Layout | **Option A**: filters above the photos; side menu unchanged except one new "archive · all photos" entry at the top of Photography (mockup: `.superpowers/brainstorm/…/content/archive-layout.html`) |
| Artist on L'Boulevard photos | Name the bands where known (Pagan Ulver, Suicide Machine from the Connection captions) |
| Audience | Art directors, cultural organisations, event organisers, potential clients |

## How it works

### Where it lives
- Route `#photography/archive`, with the filter state in a query string inside the hash: `#photography/archive?genre=concert&location=american-arts-center&year=2025`. `render()` in `index.html` must strip `?…` before splitting the route; other routes are unchanged.
- Side menu: an "archive · all photos" row with the total count at the top of the Photography section (see mockup A).
- Layout A, top to bottom: title + info line; genre row (All + parent genres); sub-genre row of the selected parent, with counts; dropdowns for place, year, event, artist (and city / client when they have options); active-filter chips + "clear all" + result count ("24 photographs", announced through an `aria-live` region); the photo grid. On phones (the existing burger breakpoint) everything except the chips and count sits behind a "Filter" button that opens a drawer.
- Grid cells: thumbnail (lazy, with `width`/`height`), a small mono caption (project or room name · date). Clicking opens the existing `#lb` viewer (`data-zoom`) with the full-size image; the viewer caption carries a link to the photo's project (`#photography/<project>`) or room (`#photography/boulevard/<room>`).
- Empty state: "No photographs match" + a reset button.
- Visual style: the site's own tokens, Archivo + IBM Plex Mono, both themes. Plain text links and underlines; the only filled element is the active chip.

### Data (in `data/`, JSON, fetched when the archive opens)
- `taxonomy.json`: the genre tree from the brief (Music, Street & Documentary, Landscape & Nature, Culture & Performing Arts and their leaves), each with id = slug and label. Photos hold leaf ids only; parents are derived.
- `refs.json`: reference tables `cities`, `locations` (with `cityId`), `events` (with `year`, optional `date`), `artists`, `clients`. Each entry: `id` (= slug), `label`.
- `photos.json`: one record per photo, the brief's shape: `id, title, image, thumb, w, h, discipline, genres[], locationId, cityId, year, date, eventIds[], artistIds[], clientId, featured, alt` plus `project` (which homepage project or room it belongs to, used for the caption and the "from …" link). `cityId` only when the location is unknown. Written one record per line so git diffs stay readable.
- `series.json`: the three rooms as curated series (Connection, Movement, Faces and Eyes) with `href` and `photoIds` in room order. Homepage projects stay curated by their order in `WORK`; they are not duplicated here.
- Validation (`validate(data)`) runs on load: unknown genre / ref id, duplicate photo id, missing image. Problems go to `console.warn` and the bad reference is ignored for filtering; the page never crashes.

### Filling the data (a one-off migration script, `scripts/fa_migrate.py`)
Only facts the site already states:
| Source | Fills |
|---|---|
| Homepage `WORK` info lines | place, date, year (e.g. "American Arts Center · 13.06.2025"); Technopark → place Technopark · Sidi Maarouf, city Casablanca, no date |
| Artist projects | artist = Ayoub Hattab, Jamila & the Other Heroes, Nanofunk, Disco Atlas, and Mehdi Ainak + Hellboy as two artists (my call: the project title names them) |
| Named nights | event = Jazz (16.05.2025), Summer Sessions (22.08.2026), Noches de Ramadán (24.02.2026), Poster Making workshop (13.02.2026); place Seamens Club for Summer Sessions; place American Arts Center for the workshop |
| Place names | "American Art Center" (workshop, Design) and "American Arts Center" (concerts) are one place: one `locations` entry labelled "American Arts Center", the brief's spelling (my call). When `pf-qsm.20` settles the name, only that label changes |
| L'Boulevard captions (`data-cap`) | year, and the festival date (Metal Day is one day: 20.09.2025 / 19.09.2026, so `date` is set and they sort with the rest), event L'Boulevard 2025 / 2026, city Casablanca, artist where the caption names the band; alt text from the room's `alt`; venue left empty (not stated) |
| Everything else | genres empty; client empty; ambiguous handles in info lines (lapero.marrokii, liquid.bridge, Jinān Al Andalus) left for the user to place in the tagging page |

Fans' Instagram handles in Faces are **not** turned into artists (my call: they are people photographed, and only the Faces room tags handles).
`x558783_464613` (`pf-qsm.35`: in Noches but really an Ayoub Hattab frame, IMG_0362, 13.06.2025) is left out of the archive until that bug is fixed, so it never carries false facts (my call). The migration has a short skip list for it.

### Images
- Thumbnails `assets/archive/t/<id>.jpg`, ~600 px on the long side, made by `scripts/fa_thumbs.py` with the Pillow Python at `~/.cache/orbit-render/v/bin/python` (my call). The script also writes `w`/`h` into `photos.json`.
- Full-size images stay where they are (`assets/home/`, each room's `images/`); `image` points there. No copies.

### Filter logic (pure functions, `assets/archive/core.js`, ES module, no DOM)
- `applyFilters(photos, state, taxonomy)`, `computeOptions(photos, state, taxonomy)`, `changeGenre(state, genre, photos, taxonomy)`, `parseUrl(hash, data)` / `serializeUrl(state)`, `validate(data)`, `sortPhotos(photos)`.
- Semantics exactly as the brief §4: OR inside one filter, AND across filters; a parent genre matches any of its leaves; `null` fields never match a filter on that field and never throw; options for each filter come from the photos matching the *other* filters, with counts; options with 0 are hidden.
- A filter group is hidden when it has fewer than two options and nothing selected in it (my call: a one-choice filter does nothing; this also hides City while everything is Casablanca, and Genre until the user tags).
- Changing genre drops only the selected values that would have 0 matches under the new genre.
- Sort: date descending, undated last, then id (stable).
- URL: slugs, comma-separated for several values; unknown params and values ignored. History policy (my call): changing genre = `pushState`, every other change = `replaceState`, so Back steps through genres. Back / Forward re-read the URL and restore the view.
- `index.html` stays a classic script; the archive UI is `assets/archive/archive.js` (module) imported from it. It exposes one function the router calls when the route is `photography/archive`.

### Tagging page (`tools/tag.html`, never linked from the site)
- Served by the same local `python3 -m http.server`; opened by URL. GitHub Pages will also serve it to anyone who guesses the address; that is harmless (it only shows public photos and cannot write to the server), so it gets `noindex` and nothing more (my call).
- Contact sheet of every photo (thumbnails); select one or several photos and edit any field: genres (checkboxes from the taxonomy), place, city, date, year, events, artists, client, featured, title, alt. Place / event / artist / client lists allow adding a new entry (written to `refs.json`). Editing several at once sets the same value on all (for tagging a whole night as Concert in one go).
- Filters on the sheet itself to find untagged photos ("no genre").
- Save: Chrome / Edge write straight into `data/photos.json` and `data/refs.json` through the File System Access API after the user picks the `data/` folder once; other browsers download both files.
- Runs `validate()` before saving and refuses to write broken references.

### Tests
- Unit: `tests/fa_core.test.mjs`, run with `node --test tests/` (Node 24 is installed; no packages). Covers every item in brief §6 "Unit tests", including validation errors.
- Fixtures: `tests/fixtures/fa/*.json`, obviously fake (`test-` ids, placeholder images). Playwright serves them in place of `data/*.json` with `page.route`, so no dev flag exists in the site code and fixtures never load in production.
- Playwright: `tests/fa_archive.py` in the repo's existing Python Playwright style, desktop 1440 and phone 390, covering brief §6 "Playwright" and acceptance criteria 1–9 (CONNECTION order is checked against `series.json`), keyboard-only filter use with visible focus, Back/Forward, and a Graphic Design smoke check.
- `tests/flow.py` gains the archive link so the existing "click everything" check still covers the whole site.

## Left to the builder
Exact CSS, dropdown component (native `<details>`/listbox vs `<select multiple>` styled), search-inside-dropdown (needed only for lists longer than ~8), thumbnail quality, how the tagging page lays out its form, file split inside `assets/archive/`.

## Open
- The user tags genres and fills the remaining places / clients after release, with the tagging page.
- Adding a new homepage project later still means a `WORK` entry; its photos then need records (the migration script can be re-run for missing ids, or the validator warns).
