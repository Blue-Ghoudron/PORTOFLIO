# F.A Filter Ability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** An Archive view (`#photography/archive`) holding all 159 photographs, filterable by genre then place / city / year / event / artist / client, with shareable URLs, plus a private tagging page to edit every photo's facts.

**Architecture:** Pure filter / URL / validation functions in one ES module (`assets/archive/core.js`, no DOM) tested with `node --test`. Data lives in four JSON files in `data/`, made once by a migration script from what the site already states. The archive UI (`assets/archive/archive.js`) is loaded by `index.html`'s router with dynamic `import()`. The tagging page (`tools/tag.html`) reuses `core.js`.

**Tech Stack:** Plain HTML/CSS/JS (no build, no packages), Node 24 built-in test runner, Python Playwright (`~/.venvs/playwright/bin/python`), Pillow via `~/.cache/orbit-render/v/bin/python` for thumbnails only.

**Spec:** `docs/specs/2026-10-21-filter-ability.md` (approved). Brief: `docs/briefs/skimart-photography-archive-brief.md`. Beads epic `pf-coe`; each task below is a child task `pf-coe.N`, and its id goes in every commit message.

## Global Constraints

- Branch `Filter-Ability`. Never commit to `Test-Fix`, `Portoflio-Branch` or `main`. Check `git status` before each commit (other sessions share the folder).
- No backend, build step, package manager or new dependency. Static files on GitHub Pages.
- Never invent facts. Unknown = `null` or `[]`. Genres start empty in the real data.
- Graphic Design (Design, Workshops menu sections) and the L'Boulevard room pages are not changed.
- Ids are slugs; URL params use slugs. Filter fields and their URL keys, in this fixed order: `genre, location, city, year, event, artist, client`. UI labels: genre, place, city, year, event, artist, client.
- Site look: existing tokens (`--bg --ink --mute --dim --line --card`), Archivo + IBM Plex Mono, both themes. The only filled element is the active chip. No rounded cards, gradients, badges.
- Fixtures never load on the real site: Playwright swaps them in with `page.route`.
- Serve with `python3 -m http.server 8026 --bind 127.0.0.1` from the repo root. Rooms live in `assets/boulevard/<room>/` (moved from `assets/boulevard/L'boulevard 26/` on 21.10.2026).
- Comments: one line, only the why, matching `index.html`'s style.

## Review Focus

1. **Back / Forward after several filter changes** — Back must step to the previous *genre* view (pushState), not replay every checkbox (replaceState), and must re-render from the URL. Test in Task 5.
2. **Hand-edited or stale URLs** (`?genre=nope&year=abc&location=american-arts-center,ghost`) — the page loads, keeps the valid values, drops the rest silently. Test in Task 2 (parse) and Task 4 (page).
3. **Photos with no genre while the user is still tagging** — they appear under All, never under a genre, never create an empty "Genre" row; with zero tagged photos the genre row is hidden entirely. Tests in Task 1 and Task 3.
4. **Re-running the migration after the user has tagged** — it must never overwrite an existing record, only add missing ones. Test in Task 3.
5. **The tagging page saving broken data** (a reference to a deleted place, a duplicate id) — save is refused with the error list shown. Test in Task 6.

---

### Task 1 (pf-coe.1): Filter core — apply, options, genre change, sort

**Files:**
- Create: `assets/archive/core.js`
- Create: `tests/fixtures/fa/taxonomy.json`, `refs.json`, `photos.json`, `series.json`, `ph.svg`
- Test: `tests/fa_core.test.mjs`

**Interfaces:**
- Produces (all exported from `core.js`; `data = {taxonomy, refs, photos, series}` exactly as the four JSON files):
  - `FIELDS = ['location','city','year','event','artist','client']`
  - `emptyState() -> {genre: null, location: [], city: [], year: [], event: [], artist: [], client: []}` (all values strings; `year` values like `'2025'`)
  - `leaves(taxonomy, genreId) -> string[]` (a parent → its children's ids; a leaf → `[id]`; null/unknown → `[]`)
  - `valuesOf(photo, field, refs) -> string[]` (location → `[locationId]`; city → `[photo.cityId ?? location.cityId]`; year → `[String(year)]`; event → `eventIds`; artist → `artistIds`; client → `[clientId]`; nulls removed)
  - `applyFilters(photos, state, data) -> photo[]` (genre: photo has any of `leaves`; per field OR, across fields AND; returns sorted)
  - `computeOptions(photos, state, data) -> {genres: [{id,label,count,children:[{id,label,count}]}], groups: {[field]: [{id,label,count}]}}` — each list from photos matching all *other* filters; zero-count entries removed; a field is absent from `groups` when it has < 2 options and nothing selected; parents with 0 are removed; labels from refs (year label = the year)
  - `changeGenre(state, genreId, photos, data) -> state` (greedy: walk `FIELDS` in order, keep each selected value only if the state kept so far + new genre + that value still matches ≥ 1 photo)
  - `sortPhotos(photos) -> photo[]` (date desc, undated last, then id asc; never mutates)
  - `slugify(label) -> string` (NFD, strip diacritics, lowercase, non-alphanumerics → `-`, trimmed)

Fixture set (write `photos.json` in the `photosJson` format of Task 2, one record per line, keys in the order `id,title,image,thumb,w,h,discipline,genres,locationId,cityId,year,date,eventIds,artistIds,clientId,featured,alt`; `thumb` = `image`; write exactly this; all images `tests/fixtures/fa/ph.svg`, `w` 400, `h` 500, `discipline` "photography", `title` "Test", `alt` "Test photo tNN", `featured` false):
- taxonomy: `music` [concert, festival], `street` [street-photography, portraits], `landscape` [landscape]
- refs: cities casablanca, rabat; locations `american-arts-center` (casablanca), `seamens-club` (casablanca), `test-venue-rabat` (rabat); events `test-fest-2025`, `test-fest-2026`, `test-night`; artists `test-band-a`, `test-band-b`; clients `test-client`
- photos (`id`: genres · locationId · cityId · year · date · eventIds · artistIds · clientId):
  - test-01: concert · american-arts-center · null · 2025 · 2025-05-16 · [] · [test-band-a] · null
  - test-02: concert · american-arts-center · null · 2026 · 2026-02-24 · [] · [] · null
  - test-03: concert, portraits · american-arts-center · null · 2026 · 2026-02-24 · [] · [test-band-b] · null
  - test-04: concert · seamens-club · null · 2026 · 2026-08-22 · [test-night] · [] · null
  - test-05: festival · null · casablanca · 2025 · 2025-09-20 · [test-fest-2025] · [test-band-a] · null
  - test-06: festival · null · casablanca · 2026 · 2026-09-19 · [test-fest-2026] · [test-band-b] · null
  - test-07: festival, portraits · null · casablanca · 2026 · 2026-09-19 · [test-fest-2026] · [] · null
  - test-08: street-photography · test-venue-rabat · null · 2025 · null · [] · [] · null
  - test-09: street-photography · null · null · null · null · [] · [] · null
  - test-10: portraits · american-arts-center · null · 2025 · 2025-06-13 · [] · [] · test-client
  - test-11: (none) · american-arts-center · null · 2026 · 2026-02-13 · [] · [] · null
  - test-12: concert · american-arts-center · null · 2025 · 2025-06-13 · [] · [test-band-a] · null
- series: `[{id:"test-series", title:"TEST SERIES", href:"#photography/boulevard/Band", photoIds:["test-07","test-05","test-06"]}]`

- [ ] **Step 1: Write the fixtures and the failing tests** in `tests/fa_core.test.mjs` (load fixtures with `fs.readFileSync` + `JSON.parse`; `ids = r => r.map(p => p.id)`):

```js
test('parent genre matches any leaf', () => assert.equal(applyFilters(P, {...emptyState(), genre:'music'}, D).length, 8));
test('AC1 concert from all places', () => assert.deepEqual(ids(applyFilters(P, {...emptyState(), genre:'concert'}, D)).sort(), ['test-01','test-02','test-03','test-04','test-12']));
test('AC2 + place narrows, AND across', () => assert.equal(applyFilters(P, {...emptyState(), genre:'concert', location:['american-arts-center']}, D).length, 4));
test('AC3 + year narrows', () => assert.deepEqual(ids(applyFilters(P, {...emptyState(), genre:'concert', location:['american-arts-center'], year:['2026']}, D)), ['test-02','test-03']));
test('OR inside a filter', () => assert.equal(applyFilters(P, {...emptyState(), location:['seamens-club','test-venue-rabat']}, D).length, 2));
test('city derived from place, or from the photo', () => assert.equal(applyFilters(P, {...emptyState(), city:['casablanca']}, D).length, 10));
test('missing metadata never matches and never throws', () => { const r = ids(applyFilters(P, {...emptyState(), year:['2025']}, D)); assert.ok(!r.includes('test-09')); });
test('AC5 empty state = whole archive', () => assert.equal(applyFilters(P, emptyState(), D).length, 12));
test('untagged photo only under All', () => assert.ok(!ids(applyFilters(P, {...emptyState(), genre:'street'}, D)).includes('test-11')));
test('sort: date desc, undated last, id tiebreak', () => assert.deepEqual(ids(sortPhotos(P)), ['test-06','test-07','test-04','test-02','test-03','test-11','test-05','test-10','test-12','test-01','test-08','test-09']));
test('options: counts from the other filters', () => { const o = computeOptions(P, {...emptyState(), genre:'concert'}, D);
  assert.deepEqual(o.groups.location.map(x => [x.id, x.count]), [['american-arts-center',4],['seamens-club',1]]);
  assert.deepEqual(o.groups.year.map(x => [x.id, x.count]), [['2025',2],['2026',3]]);
  assert.equal(o.groups.city, undefined);   // one choice and nothing selected → hidden
  assert.equal(o.groups.client, undefined); });
test('options: genres with counts, empty parent hidden', () => { const g = computeOptions(P, emptyState(), D).genres;
  assert.deepEqual(g.map(x => [x.id, x.count]), [['music',8],['street',5]]);
  assert.deepEqual(g[0].children.map(x => [x.id, x.count]), [['concert',5],['festival',3]]); });
test('options: a selected value stays listed', () => assert.ok(computeOptions(P, {...emptyState(), client:['test-client']}, D).groups.client));
test('AC4 genre change drops only zero-match values', () => assert.deepEqual(
  changeGenre({...emptyState(), genre:'concert', location:['american-arts-center'], year:['2026']}, 'festival', P, D),
  {...emptyState(), genre:'festival', year:['2026']}));
test('AC4 genre change keeps values that still match', () => assert.deepEqual(
  changeGenre({...emptyState(), genre:'concert', location:['american-arts-center'], year:['2025']}, 'portraits', P, D),
  {...emptyState(), genre:'portraits', location:['american-arts-center'], year:['2025']}));
test('genre change never leaves an empty result', () => { const s = changeGenre({...emptyState(), genre:'concert', year:['2025'], artist:['test-band-b']}, 'festival', P, D);
  assert.ok(applyFilters(P, s, D).length > 0); });
test('slugify', () => { assert.equal(slugify("L'Boulevard 2025"), 'l-boulevard-2025'); assert.equal(slugify('Jinān Al Andalus'), 'jinan-al-andalus'); });
```

- [ ] **Step 2: Run** `node --test tests/` — Expected: FAIL (`core.js` missing).
- [ ] **Step 3: Implement** the `core.js` exports listed under Interfaces. Option lists are ordered by label (years ascending); genres in taxonomy order.
- [ ] **Step 4: Run** `node --test tests/` — Expected: all pass.
- [ ] **Step 5: Commit** `pf-coe.1: archive filter core + fixtures + unit tests`.

### Task 2 (pf-coe.2): URL state and validation

**Files:**
- Modify: `assets/archive/core.js`
- Test: `tests/fa_core.test.mjs`

**Interfaces:**
- Consumes: `emptyState`, `FIELDS`, `leaves` (Task 1).
- Produces:
  - `parseQuery(query: string, data) -> state` (query without `?`; keys above, values comma-separated; drops unknown keys, unknown ids, non-existent genres, years not present in photos; never throws)
  - `serializeQuery(state) -> string` (fixed key order, empty fields omitted, `''` for the empty state, no `?`)
  - `validate(data) -> string[]` (messages like `photo test-03: unknown genre "jazz"`; checks: duplicate photo id, genre not a taxonomy leaf, unknown locationId / cityId / eventIds / artistIds / clientId, location with unknown cityId, series photoId not in photos)
  - `photosJson(photos) -> string` (`'[\n' + one JSON.stringify per record joined ',\n' + '\n]\n'`) and `refsJson(refs) -> string` (`JSON.stringify(refs, null, 1) + '\n'`) — the exact on-disk formats both the migration and the tagging page write.

- [ ] **Step 1: Write failing tests:**

```js
test('AC7 round trip', () => { const s = {...emptyState(), genre:'concert', location:['american-arts-center','seamens-club'], year:['2026']};
  const q = serializeQuery(s); assert.equal(q, 'genre=concert&location=american-arts-center,seamens-club&year=2026');
  assert.deepEqual(parseQuery(q, D), s); });
test('empty state serialises to nothing', () => assert.equal(serializeQuery(emptyState()), ''));
test('AC7 invalid params ignored', () => assert.deepEqual(
  parseQuery('genre=nope&year=abc,2025&location=american-arts-center,ghost&foo=1', D),
  {...emptyState(), year:['2025'], location:['american-arts-center']}));
test('garbage query does not throw', () => assert.deepEqual(parseQuery('%%%&&==', D), emptyState()));
test('fixtures are valid', () => assert.deepEqual(validate(D), []));
test('validation catches broken references', () => { const bad = structuredClone(D);
  bad.photos[0].genres = ['jazz']; bad.photos[1].locationId = 'ghost'; bad.photos.push({...bad.photos[2]}); bad.series[0].photoIds.push('test-99');
  const e = validate(bad).join('\n');
  for (const s of ['unknown genre "jazz"', 'unknown location "ghost"', 'duplicate id test-03', 'series test-series: unknown photo test-99']) assert.ok(e.includes(s), s); });
test('photosJson writes one record per line', () => assert.equal(photosJson(P.slice(0, 2)).split('\n').length, 5));
```

- [ ] **Step 2: Run** `node --test tests/` — Expected: the new tests FAIL.
- [ ] **Step 3: Implement** the five exports. `parseQuery` uses `URLSearchParams` inside try/catch.
- [ ] **Step 4: Run** `node --test tests/` — Expected: all pass.
- [ ] **Step 5: Commit** `pf-coe.2: archive URL state + data validation`.

### Task 3 (pf-coe.3): Real data — taxonomy, refs, migration, thumbnails

**Files:**
- Create: `data/taxonomy.json` (the brief's four parents and 18 leaves; ids = `slugify(label)`, e.g. `street-documentary`, `artist-portrait`, `night-photography`)
- Create: `scripts/fa_migrate.mjs`, `scripts/fa_thumbs.py`
- Create (generated): `data/refs.json`, `data/photos.json`, `data/series.json`, `assets/archive/t/*.jpg`
- Test: `tests/fa_data.test.mjs`

**Interfaces:**
- Consumes: `slugify`, `validate`, `photosJson`, `refsJson` (Tasks 1–2).
- Produces: the real `data/*.json` files with the exact shape the fixtures use, plus `thumb` (`assets/archive/t/<id>.jpg`), `w`, `h` (thumbnail size).

Migration rules (`node scripts/fa_migrate.mjs`):
- Read `WORK` from `index.html` (slice from `const WORK = ` to the matching `];`, evaluate with `new Function`). Read every `<button class="shot" … data-cap="…" …><img src alt>` from `assets/boulevard/{Band,Movement,Faces}/index.html` in document order.
- Homepage photo ids = the existing image ids; `image` `assets/home/<id>.jpg`; `alt` `"<project name>, photo <n>"` (the alt the site shows today); `title` null. Room photo ids `lbv-<room lower>-<file stem>`; `image` the room's `images/<file>`; `alt` the room's alt; `title` the caption's title part (e.g. "Looking up"; `null` for F/G/Study codes).
- Facts per project, exactly (refs created with these ids and labels; locations all city `casablanca`):

| project | locationId | date | eventIds | artistIds |
|---|---|---|---|---|
| technopark | `technopark-sidi-maarouf` "Technopark · Sidi Maarouf" | null | [] | [] |
| hellboy-mehdi | null | 2025-06-27 | [] | `mehdi-ainak`, `hellboy` |
| summer-sessions | `seamens-club` "Seamens Club" | 2026-08-22 | `summer-sessions` | [] |
| ayoub-hattab | `american-arts-center` "American Arts Center" | 2025-06-13 | [] | `ayoub-hattab` |
| jamila | american-arts-center | 2025-11-22 | [] | `jamila-the-other-heroes` "Jamila & the Other Heroes" |
| jazz | american-arts-center | 2025-05-16 | `jazz` | [] |
| nanofunk | american-arts-center | 2025-07-28 | [] | `nanofunk` |
| disco-atlas | american-arts-center | 2025-06-26 | [] | `disco-atlas` |
| noches | american-arts-center | 2026-02-24 | `noches-de-ramadan` | [] |
| poster-making | american-arts-center | 2026-02-13 | `poster-making-workshop` "Poster Making workshop" | [] |
| rooms, caption year 2025 / 2026 | null, `cityId` `casablanca` | 2025-09-20 / 2026-09-19 | `l-boulevard-2025` / `l-boulevard-2026` | `pagan-ulver` / `suicide-machine` when the caption contains that name |

  Only room photos set `cityId` (they have no place); everyone else gets the city through the place, and hellboy-mehdi has neither (not stated). `year` = the date's year, or null. Everything else null / `[]` / false. `genres` `[]`.
- Skip `x558783_464613` (`pf-qsm.35`); skip the Design section and `boulevard` overview entry.
- Keep existing records: if `data/photos.json` exists, records already in it are left untouched and only missing ids are appended; refs are merged by id the same way.
- `series.json`: `connection` "Connection" `#photography/boulevard/Band`, `movement` "Movement" `#photography/boulevard/Movement`, `faces-and-eyes` "Faces and Eyes" `#photography/boulevard/Faces`, each `photoIds` in room order.
- Ends with `validate()`; exits 1 and prints the errors if any.

`~/.cache/orbit-render/v/bin/python -I scripts/fa_thumbs.py`: for each record without an existing thumbnail file, make a 600 px long-side JPEG (quality 82, `ImageOps.exif_transpose`) at `thumb`, and write `w`/`h` back into `photos.json` using the same one-record-per-line format.

- [ ] **Step 1: Write failing tests** in `tests/fa_data.test.mjs` (reads the real `data/`):

```js
test('159 photos, all valid', () => { assert.equal(D.photos.length, 159); assert.deepEqual(validate(D), []); });
test('every image and thumb exists, with size', () => { for (const p of D.photos) { assert.ok(existsSync(p.image), p.image); assert.ok(existsSync(p.thumb), p.thumb); assert.ok(p.w > 0 && p.h > 0, p.id); } });
test('no invented genres yet', () => assert.ok(D.photos.every(p => p.genres.length === 0)));
test('misfiled Noches photo left out', () => assert.ok(!D.photos.some(p => p.id === 'x558783_464613')));
test('facts copied, not invented', () => { const by = Object.fromEntries(D.photos.map(p => [p.id, p]));
  assert.deepEqual([by.x839456_462094.locationId, by.x839456_462094.date, by.x839456_462094.artistIds], ['american-arts-center', '2025-06-13', ['ayoub-hattab']]);
  assert.equal(by.x714252_433206.date, null);
  assert.deepEqual(by['lbv-band-frame-02'].artistIds, ['suicide-machine']);
  assert.equal(by['lbv-band-frame-02'].locationId, null); });
test('room series keep room order', () => assert.equal(D.series.find(s => s.id === 'connection').photoIds[0], 'lbv-band-frame-03'));
test('with nothing tagged the genre row is hidden', () => assert.deepEqual(computeOptions(D.photos, emptyState(), D).genres, []));
test('re-running migration keeps edited records', () => { /* copy data/ to a temp dir, set genres on one record, run the script with FA_DATA=<tmp> via execFileSync, assert the record and count are unchanged */ });
```

  (The script reads its data dir from `process.env.FA_DATA || 'data'` so the last test runs on a copy.)
- [ ] **Step 2: Run** `node --test tests/` — Expected: data tests FAIL (no data).
- [ ] **Step 3: Write** `data/taxonomy.json`, `scripts/fa_migrate.mjs`, `scripts/fa_thumbs.py`; run `node scripts/fa_migrate.mjs` then the thumbs script.
- [ ] **Step 4: Run** `node --test tests/` — Expected: all pass. Open `data/photos.json` and spot-check 5 records by eye against the site.
- [ ] **Step 5: Commit** `pf-coe.3: archive data from the site's own facts + thumbnails` (thumbnails included).

### Task 4 (pf-coe.4): Archive view — desktop

**Files:**
- Create: `assets/archive/archive.js`, `assets/archive/archive.css`
- Modify: `index.html` — `<link>` to `archive.css` in `<head>`; `render()` (`index.html:274`) hash parsing + archive branch; nav building (`index.html:248`) archive row; viewer `show()` / `openLb` (`index.html:336-340`) full-size image + "from" link; `#lb` markup gets `<a id="lb-from" hidden></a>`
- Test: `tests/fa_archive.py`

**Interfaces:**
- Consumes: everything in `core.js`.
- Produces: `export async function showArchive(view: HTMLElement, query: string, work: Array)` in `archive.js`. Data is fetched once (`data/taxonomy.json`, `refs.json`, `photos.json`, `series.json`) and cached; `validate()` problems go to `console.warn`. `index.html` calls it as:

```js
const [path, query = ''] = location.hash.slice(1).split('?'), [sid, pid, room] = path.split('/');
// …
if (sid === 'photography' && pid === 'archive') { import('./assets/archive/archive.js').then(m => m.showArchive(view, query, WORK)); /* aria-current on the row, close the phone menu */ }
```

Markup contract (tests and Task 5–6 rely on these selectors):
- `section.proj.archive` › `h2` "Archive", `p.info` "Every photograph · filter by genre, place, year, event".
- Genre row `nav.fa-genres` › `button[data-genre=""]` "All" + one `button[data-genre=<parent>]` per visible parent, `aria-pressed`; sub row `div.fa-sub` › `button[data-genre=<leaf>]` "concert (5)" for the selected parent (or the parent of the selected leaf). Whole genre block absent when `genres` is empty.
- One `details.fa-dd[data-field=<field>]` per visible group, `summary` "place ▾" / "place: American Arts Center ▾" / "place: 2 ▾"; inside, `label > input[type=checkbox][value=<id>]` + label + `span.n` "(4)"; a `input[type=search]` filter on top when the group has > 8 options.
- `div.fa-chips` › `button.fa-chip[data-field][data-value]` "American Arts Center ×", `button.fa-clear` "clear all" (only when something is selected), `p.fa-count[aria-live=polite]` "24 photographs" / "1 photograph".
- `div.grid.fa-grid` › `figure[data-zoom][data-id]` › `img` (src `encodeURI(thumb)`, `data-full` `encodeURI(image)`, `width`/`height`, `loading=lazy`, `alt`) + `figcaption.cam` "Jazz · 16.05.2025" (from-label · date as dd.mm.yyyy, else year, else nothing).
- Empty: `div.fa-empty` "No photographs match" + `button.fa-reset` "reset filters".
- From-label: the `WORK` project whose `imgs` contains the id (name, `#photography/<id>`), else the series containing it (title, href).
- History: genre buttons → `history.pushState(null, '', '#photography/archive' + (q ? '?' + q : ''))`; every other change → `replaceState`. Then re-render the archive in place (no full `render()`).
- Menu: first row of the Photography section `li > a.arch[href="#photography/archive"]` "archive · all photos" with the total count, styled like mockup A.
- Viewer: `show()` uses `img.dataset.full || img.src`; `#lb-from` shows "from Jazz →" linking the from-href when the figure has `data-from-href`, and closes the viewer on click.

- [ ] **Step 1: Write the failing Playwright test** `tests/fa_archive.py` (style of `tests/flow.py`; fixtures served with `page.route('**/data/*.json', …)` from `tests/fixtures/fa/`; desktop 1440×900). Helper `count()` reads `.fa-count`; `state()` reads `location.hash`. Checks, each an `ok(cond, msg)`:
  - AC1 click `[data-genre=music]` then `[data-genre=concert]` → "5 photographs"
  - AC2 open place, tick `american-arts-center` → "4 photographs", chip present, no `[data-genre=american-arts-center]` anywhere
  - AC3 tick year 2026 → "2 photographs", hash `#photography/archive?genre=concert&location=american-arts-center&year=2026`
  - AC4 click `[data-genre=music]` then `[data-genre=festival]` → place chip gone, year chip kept, "2 photographs"
  - AC5 `.fa-clear` → "12 photographs"
  - AC6 `test-05` figure present under festival; opening it shows `#lb-from` linking `#photography/boulevard/Band`
  - AC7 load `…#photography/archive?genre=concert&location=american-arts-center&year=2026` fresh → "2 photographs" and both chips; load `?genre=nope&year=abc` → "12 photographs", no `pageerror`
  - AC8 no `details.fa-dd[data-field=city]` under concert; no group with zero options; empty state shown by route-patching photos to `[]` → `.fa-empty` with working reset
  - viewer opens the `data-full` image
  - real data (no route): archive row in the menu says 159, the page shows "159 photographs", no genre block, no console errors
- [ ] **Step 2: Run** server + `~/.venvs/playwright/bin/python -I tests/fa_archive.py` — Expected: FAIL (no archive).
- [ ] **Step 3: Implement** `archive.js`, `archive.css` and the `index.html` changes per the contract.
- [ ] **Step 4: Run** `tests/fa_archive.py`, `node --test tests/` and `tests/flow.py` — Expected: `FAILS: none`, all pass.
- [ ] **Step 5: Commit** `pf-coe.4: archive view (desktop) + router + viewer link`.

### Task 5 (pf-coe.5): Phone drawer, keyboard, Back/Forward, site-wide check

**Files:**
- Modify: `assets/archive/archive.js`, `assets/archive/archive.css`, `tests/flow.py`
- Test: `tests/fa_archive.py`

**Interfaces:**
- Consumes: Task 4's markup contract.
- Produces: `button.fa-open[aria-expanded][aria-controls=fa-panel]` "Filter" (shown ≤ 820 px), `div#fa-panel` holding genres + dropdowns, closed by `button.fa-done` "show N photographs" or Escape; chips and count stay outside the panel.

- [ ] **Step 1: Extend `tests/fa_archive.py`** with a phone project (390×844) and these checks:
  - phone: `.fa-open` visible, panel hidden; open → pick concert + place → `.fa-done` says "show 4 photographs" → panel closes, focus returns to `.fa-open`, grid shows 4
  - keyboard only (desktop): Tab reaches "All", genre buttons, each `summary`, checkboxes (Space toggles), chips, clear all; every focused element has a visible outline (`getComputedStyle(el).outlineStyle !== 'none'`)
  - Back/Forward: All → music → concert → tick place → tick year; `go_back()` → genre music with no place/year in the hash and "8 photographs"; `go_forward()` → concert view restored
  - Graphic Design smoke: `#design/personal` and `#workshops/poster-making` render their grids unchanged (same figure counts as before: 29 and 16)
- [ ] **Step 2: Run** — Expected: phone and Back checks FAIL.
- [ ] **Step 3: Implement** the drawer, focus handling, and a `hashchange`-driven re-read (the router already calls `showArchive` on `hashchange`; make it reuse cached data and keep scroll at top). Add the archive link to `tests/flow.py`'s menu clicks at all three sizes.
- [ ] **Step 4: Run** `tests/fa_archive.py`, `tests/flow.py`, `node --test tests/` — Expected: all pass, `FAILS: none`.
- [ ] **Step 5: Commit** `pf-coe.5: archive phone drawer, keyboard, history`.

### Task 6 (pf-coe.6): Tagging page

**Files:**
- Create: `tools/tag.html`, `tools/tag.js`, `tools/tag.css`
- Test: `tests/fa_tag.py`

**Interfaces:**
- Consumes: `validate`, `slugify`, `photosJson`, `refsJson`, `leaves` from `../assets/archive/core.js`; the four data files via `fetch('../data/…')`.
- Produces: a page at `http://localhost:8026/tools/tag.html`, `<meta name="robots" content="noindex">`, linked from nowhere.

Behaviour:
- Contact sheet of every photo (thumb + id + genre count). Click selects one; Shift/Ctrl-click adds. Toolbar: "only untagged" toggle (no genres), text search on id / project.
- Form for the selection: genres (checkboxes by parent), place (select + "new…"), city (select + "new…"), date (`input[type=date]`; year follows the date, or a year field when there is no date), events / artists (checkbox lists + "new…"), client (select + "new…"), featured, title, alt. With several photos selected a field showing "mixed" changes only when edited; ticking a list item adds it to all, unticking removes it from all.
- "New…" asks for a label, makes `{id: slugify(label), label}` (place also asks the city; event also asks the year), refuses an id that exists.
- Save: `validate()` first — if errors, list them in `#errors` and write nothing. Then, if `showDirectoryPicker` exists, ask once for the `data/` folder and write `photos.json` / `refs.json` with `photosJson` / `refsJson`; otherwise download both files.
- Unsaved changes → `beforeunload` warning.

- [ ] **Step 1: Write the failing test** `tests/fa_tag.py` (fixtures via `page.route`; `add_init_script('delete window.showDirectoryPicker')` to force downloads):
  - select test-11 and test-02 → tick `festival` → Save → downloaded `photos.json` has `festival` in both records' genres and every other record byte-identical to the fixture line
  - add a new artist "Test Band C" → saved refs contain `{"id":"test-band-c","label":"Test Band C"}`
  - Review Focus 5: inject a broken record (`page.evaluate` sets a photo's `locationId` to `ghost`) → Save shows `unknown location "ghost"` and no download happens
- [ ] **Step 2: Run** — Expected: FAIL.
- [ ] **Step 3: Implement** the page.
- [ ] **Step 4: Run** `tests/fa_tag.py` — Expected: pass. Then open it in Chrome by hand against the real `data/` and save once to check the folder-writing path leaves `git diff data/` empty.
- [ ] **Step 5: Commit** `pf-coe.6: tagging page for archive metadata`.

### Task 7 (pf-coe.7): Docs, full run, review, PR

**Files:**
- Modify: `CLAUDE.md` (Architecture: Archive + data files + tagging page + how to add photos; Run and test: `node --test tests/`, `tests/fa_archive.py`, `tests/fa_tag.py`)
- Modify: `docs/specs/2026-10-21-filter-ability.md` (Status: built)

- [ ] **Step 1:** Run every check: `node --test tests/`, `tests/fa_archive.py`, `tests/fa_tag.py`, `tests/flow.py`. Expected: all pass. Save the output for the PR.
- [ ] **Step 2:** `/playwright-testing` pass by hand: archive at 390 / 820 / 1440 in both themes, every menu link clicked; screenshots to `tests/out/fa/`.
- [ ] **Step 3:** Review the whole diff against brief §6–7 (requesting-code-review); fix findings; report any deviation from the brief.
- [ ] **Step 4:** Update the docs, commit `pf-coe.7: docs for the archive`, push.
- [ ] **Step 5:** Open the PR `Filter-Ability` → `Portoflio-Branch` with summary, beads tasks, test results, known limits (genres untagged; `pf-qsm.35` photo left out; Test-Fix's menu/grid changes will need merging). **Ask the user before merging.**
