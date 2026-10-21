# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

SKIMART portfolio (Ghoujlami Mohamed, photographer / visual artist, Casablanca): a static site in plain HTML, CSS and JS. No build step, no package manager, no dependencies.

## Run and test

```bash
python3 -m http.server 8026 --bind 127.0.0.1    # from the repo root, then open http://localhost:8026/
```

Always serve over http, not `file://`: the homepage reads the L'Boulevard iframe's document to sync themes, and browsers block that on `file://`.

```bash
~/.venvs/playwright/bin/python -I tests/flow.py [base-url]    # default http://localhost:8026/; exit 1 + FAILS list on any break
```

`tests/flow.py` clicks every menu link, the CTA, About, logo, burger, theme switch and photo viewer, every room inside the L'Boulevard frame, and every Boulevard page's nav, theme and handles, at 390, 820 and 1440 px. Run it before saying a page change is done. Archive (F.A) checks: `node --test 'tests/*.test.mjs'` (filter logic + real data), `tests/fa_archive.py` and `tests/fa_tag.py` (Playwright, on the fake photos in `tests/fixtures/fa/`; same `[base-url]` argument). Other checks are `tests/pf-qsm.<n>_*.py` (one per beads task); their reports are in `docs/reports/`. Screenshots go to the gitignored `tests/out/` and `tests/screens/`.


## Architecture

### Homepage: `index.html` (one file, hash router)
- All content lives in the `WORK` array: sections → projects → image ids. Image `<id>` is `assets/home/<id>.jpg` (resized to 1600 px). Projects with a `group` are nested under that group in the side menu. To add a project, add an entry and its images; nothing else.
- `render()` runs on `hashchange`. Routes: `#about`; `#<section>/<project>` (photo or poster grid); `#photography/boulevard[/<room>]`, which shows the L'Boulevard exhibition in an `<iframe>` (`BOULEVARD/<room>/index.html`). The project with `boulevard:true` appears in the menu as one link with an "exhibition" tag.
- Theme: `data-theme` on `<html>`, saved in localStorage `skm-theme`, else the system setting. While the exhibition is open, `body.lbv-on` switches the portfolio to the exhibition palette and follows its switch through a `MutationObserver` on the iframe's `<html data-theme>` (same origin only).
- Photo viewer: any `[data-zoom]` element opens the full-screen `#lb` viewer (arrows, swipe, click to zoom 2×).
- The design brief is `Briefs/Homepage Implementation Brief.txt`: photographer first, editorial, minimal; near-black / off-white. Don't invent project descriptions, clients or credits.

### Archive: `#photography/archive` (F.A, spec `docs/specs/2026-10-21-filter-ability.md`)
- Every photograph (homepage photo projects, Workshops, L'Boulevard rooms) in one view: genre first, then place / city / year / event / artist / client. A place is never a genre.
- Data in `data/`: `taxonomy.json` (genre tree; photos hold leaf ids only), `refs.json` (places, cities, events, artists, clients), `photos.json` (one record per line), `series.json` (the rooms, in room order). Unknown facts stay `null`; never invent them.
- Logic in `assets/archive/core.js` (pure, unit-tested), view in `assets/archive/archive.js` + `archive.css`, loaded by `render()` with `import()`. Filters live in the address (`#photography/archive?genre=concert&year=2026`): a genre change is a history step, ticking a box is not.
- Thumbnails `assets/archive/t/<id>.jpg`. New photos: add them to `WORK` / a room as usual, then `node scripts/fa_migrate.mjs` (only appends missing records) and `~/.cache/orbit-render/v/bin/python -I scripts/fa_thumbs.py`.
- Tagging: `tools/tag.html` on the local server (not linked from the site) edits every field; Chrome/Edge save straight into `data/`, other browsers download the two files.

### Exhibition: `BOULEVARD/`
- Photos from L'Boulevard's Metal Day (20.09.2025 and 19.09.2026). The hub is `index.html` (one door per room). The rooms are `Movement/`, `Band/` (titled **Connection**) and `Faces/` (Faces and Eyes). Each room is a self-contained page with its own CSS, JS and `images/`.
- Shared files: `theme.js` (light/dark, localStorage `lbv-theme`) and `Band/assets/` (film grain, wireframe SVGs; other rooms use `../Band/assets/...`).
- Every page's `.pages` nav lists every page. A new room must be added to every nav and get a door on the hub. New rooms are built with the `lboulevard` skill (`~/.claude/skills/lboulevard`, images made from the Lightroom exports with `scripts/lbv.py`).
- Pages must work both standalone and inside the homepage iframe.
- Palette (keep it): wall `#251726`, ink/mat `#EEFFE5`, blue `#337aff` (small text `#3d81ff`). The light theme is a `:root[data-theme="light"]` token block in each page. Prints have a 41 px `#EEFFE5` mat.
- Pages are about the photographs, not the bands: no band name as a title. Only Faces tags people's Instagram handles. Say each fact once; the user dislikes repeated words.
- `TASKS.md` / `TASKS-phone.md` hold the history of past passes.

Never touch `Band/screenshots/`. The photo sources in `C:\Users\ghouj\SKIMART` (`/mnt/c/...`) are read-only.

## Workflow

- Tasks live in **beads** (`bd list`, `bd ready`, `bd show <id>`), as a graph: a task can depend on others. The current plan is epic `pf-qsm` (tests, critique, redesign, fixes). Label `agent` = can run as a parallel subagent, read-only on the site (writes only `tests/<task-id>_*.py` and a report). Label `main` = done in the main session, because it edits the site or needs approval.
- Name every subagent or session after its task, e.g. `pf-qsm.4 Accessibility audit`.
- Specs go in `docs/specs/YYYY-MM-DD-<topic>.md` and are written before building.
- Order: plan → the user approves → implement → review → PR. Never merge without asking.
- Branches: finished work is pushed to `Portoflio-Branch` (homepage and exhibition, PR #2 to `main`). `Test-Fix` (worktree `~/projects/PORTOFLIO-Fixes`, formerly `Portoflio-Fixes`) is only for test runs and fix passes. Feature branches (e.g. `Filter-Ability`) branch off `Portoflio-Branch`. `Portoflio-Branch` has no checkout of its own: commit through a temporary `git worktree add`. Several Claude sessions often work in this folder at once: check `git status` before committing, and don't switch branches under another session's feet.
