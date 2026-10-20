# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

SKIMART portfolio (Ghoujlami Mohamed, photographer / visual artist, Casablanca): a static site in plain HTML, CSS and JS. No build step, no package manager, no dependencies.

## Run and test

```bash
python3 -m http.server 8026 --bind 127.0.0.1    # from the repo root, then open http://localhost:8026/
```

Always serve over http, not `file://`: the homepage reads the L'Boulevard iframe's document to sync themes, and browsers block that on `file://`.

There are no tests in the repo yet (beads task `pf-qsm.1` adds `tests/flow.py`). Until then, use the `playwright-testing` skill (Playwright venv in `~/.venvs/playwright`):

```bash
~/.venvs/playwright/bin/python ~/.claude/skills/playwright-testing/scripts/qa_check.py \
  "http://localhost:8026/index.html" "http://localhost:8026/BOULEVARD/L'boulevard%2026/Band/index.html" --links --out <dir>
```

Before saying a page change is done, click every link and button (`#work` links, CTA, about, logo, burger, `#theme`, the photo viewer; on Boulevard pages `.pages a`, `.handles a`, `#theme`) at 390, 820 and 1440 px.

Paths contain an apostrophe and a space (`BOULEVARD/L'boulevard 26`): quote them in the shell and write `L'boulevard%2026` in URLs.

## Architecture

### Homepage: `index.html` (one file, hash router)
- All content lives in the `WORK` array: sections → projects → image ids. Image `<id>` is `assets/home/<id>.jpg` (resized to 1600 px). Projects with a `group` are nested under that group in the side menu. To add a project, add an entry and its images; nothing else.
- `render()` runs on `hashchange`. Routes: `#about`; `#<section>/<project>` (photo or poster grid); `#photography/boulevard[/<room>]`, which shows the L'Boulevard exhibition in an `<iframe>` (`BOULEVARD/L'boulevard 26/<room>/index.html`). The project with `boulevard:true` appears in the menu as one link with an "exhibition" tag.
- Theme: `data-theme` on `<html>`, saved in localStorage `skm-theme`, else the system setting. While the exhibition is open, `body.lbv-on` switches the portfolio to the exhibition palette and follows its switch through a `MutationObserver` on the iframe's `<html data-theme>` (same origin only).
- Photo viewer: any `[data-zoom]` element opens the full-screen `#lb` viewer (arrows, swipe, click to zoom 2×).
- The design brief is `Homepage Implementation Brief.txt`: photographer first, editorial, minimal; near-black / off-white. Don't invent project descriptions, clients or credits.

### Exhibition: `BOULEVARD/L'boulevard 26/`
- Photos from L'Boulevard's Metal Day (20.09.2025 and 19.09.2026). The hub is `index.html` (one door per room). The rooms are `Movement/`, `Band/` (titled **Connection**) and `Faces/` (Faces and Eyes). Each room is a self-contained page with its own CSS, JS and `images/`.
- Shared files: `theme.js` (light/dark, localStorage `lbv-theme`) and `Band/assets/` (film grain, wireframe SVGs; other rooms use `../Band/assets/...`).
- Every page's `.pages` nav lists every page. A new room must be added to every nav and get a door on the hub. New rooms are built with the `lboulevard` skill (`~/.claude/skills/lboulevard`, images made from the Lightroom exports with `scripts/lbv.py`).
- Pages must work both standalone and inside the homepage iframe.
- Palette (keep it): wall `#251726`, ink/mat `#EEFFE5`, blue `#337aff` (small text `#3d81ff`). The light theme is a `:root[data-theme="light"]` token block in each page. Prints have a 41 px `#EEFFE5` mat.
- Pages are about the photographs, not the bands: no band name as a title. Only Faces tags people's Instagram handles. Say each fact once; the user dislikes repeated words.
- `TASKS.md` / `TASKS-phone.md` hold the history of past passes. `L'boulevard 25/` is empty.

Never touch `Band/screenshots/`. The photo sources in `C:\Users\ghouj\SKIMART` (`/mnt/c/...`) are read-only.

## Workflow

- Tasks live in **beads** (`bd list`, `bd ready`, `bd show <id>`), as a graph: a task can depend on others. The current plan is epic `pf-qsm` (tests, critique, redesign, fixes). Label `agent` = can run as a parallel subagent, read-only on the site (writes only `tests/<task-id>_*.py` and a report). Label `main` = done in the main session, because it edits the site or needs approval.
- Name every subagent or session after its task, e.g. `pf-qsm.4 Accessibility audit`.
- Specs go in `docs/specs/YYYY-MM-DD-<topic>.md` and are written before building.
- Order: plan → the user approves → implement → review → PR. Never merge without asking.
- Branches: fixes go on `Portoflio-Fixes` (made from `Portoflio-Branch`). `Portoflio-Branch` holds the homepage and the exhibition (PR #2 to `main`). Several Claude sessions often work in this folder at once: check `git status` before committing, and don't switch branches under another session's feet.
