# Page editor (`tools/pages.html`)

Edit a homepage page's photos by hand, on the local server, like `tools/tag.html` (not linked from the site).

## What it does
- Pick a page: any project in `WORK` (a project with categories, e.g. Personal project, is edited one category at a time). L'Boulevard rooms are not here (their pages are built with the `lboulevard` skill).
- See its photos in order. Drag (or ← →) to reorder, × to remove, set the menu photo (`th`), tick **featured** (home preview + Photography page).
- New page: section, name, menu group (photography; an existing one or a new one), optional line under the title. Its WORK line goes after the last page of its group, else at the end of the section; it is only saved with at least one photo (the menu shows the first).
- Page order (one per section): every page as a tile under its menu group, in menu order. ← → or drag moves a page inside its group, ↑ ↓ moves a whole group. Save rewrites the order of that section's `WORK` lines (a page spanning several lines moves whole); the menu lists groups in order of their first page.
- Add photos from files: each JPG is resized in the browser to 1600 px (`assets/home/<page>-<n>.jpg`) with a 600 px archive thumbnail. Its camera line comes from the file's own EXIF when it has one (camera JPGs do, Lightroom exports usually don't; `scripts/add_page.py` remains the way to get lines from the originals).
- Save writes, in Chrome/Edge, into the site folder picked once: new images, `index.html` (the page's `imgs` and `th`), `assets/home/labels.js` (+ its `?v=` cache-buster), `data/photos.json` (archive records of photo pages: added, removed, renumbered alt, featured). Removed photos' files are deleted when nothing else uses them. Other browsers: no save (too many files to download).

## Rules
- Same record shape and file formats as `add_page.py` / `fa_migrate.mjs` (photos.json one record per line). Tags people set are never touched.
- Poster pages (Design) have no archive records and no camera lines.
- The text edits live in `tools/pages-core.js` (pure, unit-tested in `tests/pages.test.mjs`); `tools/pages.js` is the page.
