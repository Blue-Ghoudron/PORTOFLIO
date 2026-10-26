# SKIMART Portfolio — Photography Archive & Smart Filtering

## Working agreement

- Act as a senior developer (use the **ponytail** skill): question unclear requirements, prefer simple and maintainable solutions, avoid over-engineering, and flag risks early.
- Use **beads** for all task tracking (see section 8).
- Use **Playwright** for end-to-end testing (see section 6).
- Follow my **workflow skill** for the overall process (see section 8).

## 1. Objective

Build a photography portfolio organized as a curated visual archive. Visitors browse photographs by genre, then refine results using metadata such as location, year, event, and artist.

The system must separate **what a photograph is about** (genre) from **where, when, and for whom it was created** (metadata).

Example: A concert photographed at the American Arts Center belongs to the genre `Concert` (under `Music`). Its location is `American Arts Center`, its city is `Casablanca`, and its year is `2026`. AAC must never become a genre merely because many photographs were taken there.

## 2. Information Architecture

### A. Disciplines

- Photography (primary focus, covered by this brief)
- Graphic Design: leave its content, pages, and design untouched. It only needs to keep working alongside the new discipline structure. Do not apply the genre/filter system to it.

### B. Genre taxonomy

Genres live in a separate taxonomy file, not inside photo records. The taxonomy defines the hierarchy; photos reference **leaf genre IDs only**, and parent genres are derived.

Starting taxonomy (configurable, not mandatory for every image):

- **Music:** Concert, Festival, Live Performance, Rehearsal, Artist Portrait
- **Street & Documentary:** Street Photography, Urban Life, Portraits, Documentary, Architecture
- **Landscape & Nature:** Landscape, Urban Landscape, Nature, Night Photography
- **Culture & Performing Arts:** Dance, Theatre, Exhibition, Cultural Events

Rules:
- A photo may have several leaf genres when justified (e.g. `["concert", "artist-portrait"]`).
- Selecting a parent (Music) matches every photo tagged with any of its children.
- Adding a location, event, or year must never require a new genre.

### C. Reference tables (single source of truth)

Metadata that repeats across photos lives in reference tables with stable IDs, slugs, and display labels. Photos point to IDs, never to free-text strings, so spelling variants cannot split a filter.

- **locations** (id, slug, label, cityId): American Arts Center, Boultek, Place des Nations Unies, etc.
- **cities** (id, slug, label): Casablanca, Rabat, etc.
- **events** (id, slug, label, year, optional date): L'Boulevard 2025, Jazzablanca, etc.
- **artists** (id, slug, label): performers, bands, people, subjects
- **clients** (id, slug, label): commissioning organizations
- **series** (see section 5)

Fields on each photograph itself: `year`, `date` (exact, when known), `featured`, `alt`, `title`, `image`.

## 3. Photograph Data Model

Store metadata separately from gallery presentation. Illustrative shape (adapt to the existing architecture):

```json
{
  "id": "lb-2026-001",
  "title": "Untitled",
  "image": "/images/photography/lb-2026-001.jpg",
  "discipline": "photography",
  "genres": ["concert"],
  "locationId": "boultek",
  "cityId": null,
  "year": 2026,
  "date": null,
  "eventIds": ["l-boulevard-2025"],
  "artistIds": [],
  "clientId": null,
  "featured": false,
  "alt": "Description of the photograph"
}
```

Field cardinality:
- **Arrays:** `genres`, `eventIds`, `artistIds`
- **Single value:** `locationId`, `cityId`, `clientId`, `year`, `date`
- `cityId` on a photo is only used when the location is unknown; otherwise the city is derived from the location.
- Series membership is **not** stored on the photo; it comes from the series file (section 5), so there is one source of truth.

Rules:
- Unknown metadata stays `null` or empty. Never invent locations, dates, events, artists, or descriptions.
- Validate all references at build or load time (unknown genre ID, missing location, duplicate photo ID) and report clear errors without crashing the site.
- Prefer a structured content file or CMS over hardcoding filters into the UI.

## 4. Filtering Experience

Provide a clear filter interface above the photography gallery.

Example path: Photography → Music → Concert, then refine by Location: American Arts Center, Year: 2026, Event, Artist.
Another: Music → Festival → L'Boulevard → 2025.

### Filter semantics

- **Within one filter:** OR (selecting two locations shows photos from either).
- **Across filters:** AND (location + year narrows to photos matching both).
- **Genre:** selecting a parent matches any of its leaf children; selecting a leaf matches that leaf.
- **Missing metadata:** a photo with `null` for a field simply doesn't match filters on that field and never breaks anything.
- **Sorting:** stable, with a deterministic tiebreaker (e.g. date descending, then ID).

### Dynamic options

- Each filter's available options are computed from the set of photos matching the **other** active filters.
- Show a count next to each option (e.g. `Boultek (12)`).
- Hide options and entire filter groups with zero matches; never show empty or irrelevant categories.
- **Changing genre:** after the change, drop any selected filter value that now has zero matches under the new genre. Keep values that still match. Selected values must never silently produce an empty result because of a genre switch.

### UI requirements

- Genre navigation with expandable subcategories.
- Searchable dropdowns for locations, events, and artists.
- Multi-select where appropriate; year selection.
- Visible active-filter chips and a clear-all action.
- Result count (e.g. `24 photographs`).
- Empty state with a reset option.
- Mobile-friendly filter drawer or collapsible panel.
- Gallery updates without a full page reload.

### URL state

- Filters are stored in query parameters using **slugs**, not display names (e.g. `?genre=concert&location=american-arts-center&year=2026`). Multiple values for one filter are comma-separated or repeated.
- Loading a URL restores the exact view.
- Unknown or invalid parameters and values are ignored silently; the page must still load.
- Changing a filter uses `replaceState` for rapid refinements (typing in search, toggling chips) and `pushState` for meaningful navigation changes (e.g. switching genre), so Back behaves sensibly. Pick one consistent policy and document it.

## 5. Curated Projects vs. Filtered Archive

Two complementary experiences:

**Curated Projects:** Editorially selected series with intentional order, cover, title, and description (CONNECTION, MOVEMENT, FACES, EYES).
**Photography Archive:** The full searchable collection, filterable by genre, location, year, event, artist, and client.

Series data lives in its own file:

```json
{
  "id": "connection",
  "slug": "connection",
  "title": "CONNECTION",
  "description": "Editorial description, kept separate from filter labels.",
  "coverPhotoId": "lb-2026-001",
  "photoIds": ["lb-2026-001", "lb-2026-014", "..."]
}
```

- The order of `photoIds` **is** the intended sequence. Series pages render in that order and are never auto-sorted chronologically.
- A series is not a genre. CONNECTION may span stage performances and audience reactions across years, and its photos still appear in normal genre-filtered archive results based on their own genres.
- The archive may optionally offer Series as an additional filter; it follows the same rules as the other metadata filters.

## 6. Technical Requirements

- **First inspect the existing repository, framework, and current image/project data structures.** Reuse existing components and dependencies. Preserve the current visual identity and responsive layout.
- Constraints: [fill in: static hosting / no backend / framework preferences / existing build tooling].
- Implement filtering as pure, composable functions (e.g. `applyFilters(photos, state)`, `computeOptions(photos, state)`, `parseUrl` / `serializeUrl`) rather than separate hardcoded gallery pages.
- Accessible labels, keyboard navigation, visible focus states, and announced result-count updates.
- Optimize image loading: thumbnails, lazy loading, explicit dimensions to avoid layout shift.
- Keep original image metadata and editorial descriptions separate from filter labels.

### Test data

- Fixtures live in a clearly separate file (e.g. `photos.fixtures.json`) and are obviously fake (placeholder titles, placeholder images, IDs prefixed `test-`).
- Fixtures are used only by tests and an optional dev flag, and **never ship in production data**.
- Do not create fake photography, project details, or capture dates in the real content files.

### Testing

**Unit tests** (write them and report results) cover the pure filter, option, and URL functions, at minimum:
- Genre parent/child matching
- OR within a filter, AND across filters
- Dynamic options and counts
- Dropping incompatible filter values when genre changes
- Missing metadata (null location, no artists, no date)
- URL parse and serialize round trip, plus invalid-parameter handling
- Reference validation errors

**Playwright end-to-end tests** cover the real UI, run against fixture data (never production data):
- Each acceptance criterion in section 7 that is user-visible (1 to 9)
- Filter combinations: genre → location → year, then genre change dropping zero-match values
- URL restore: load a filtered URL and verify the exact view; load a URL with invalid params and verify the page still renders
- Empty state and reset, clear-all, and active-filter chips
- Curated series page shows photos in the defined order
- Keyboard-only navigation of the filter UI and visible focus states
- Both desktop and mobile viewports (run as separate Playwright projects); on mobile, verify the filter drawer opens, applies filters, and closes
- A smoke test that the Graphic Design pages still load unchanged

## 7. Acceptance Criteria

1. Selecting `Music → Concert` shows concert photographs from all locations.
2. Selecting `American Arts Center` narrows those results without treating AAC as a genre.
3. Selecting `2026` narrows them further.
4. Changing the genre drops only the selected values that have zero matches under the new genre and keeps the rest.
5. Clearing all filters restores the complete archive.
6. CONNECTION is accessible as a curated series in its defined order and also appears in appropriate genre-filtered results.
7. The current filter selection can be shared and restored via URL, and invalid parameters are ignored without errors.
8. Missing metadata causes no crashes and no misleading or empty filter options.
9. The system works on desktop and mobile.
10. Existing portfolio content, Graphic Design, and visual design are preserved unless a change is explicitly required.
11. All unit tests pass.
12. All Playwright tests pass on desktop and mobile projects, and results are reported.

## 8. Process

Follow my workflow skill: **plan → ask for approval → implement → review → create pull request → ask for merge.** Do not skip or reorder steps.

1. **Discovery:** Inspect the codebase and identify the existing image and project data structures. Then run the **grill-me** skill and resolve any open questions with me before planning. Do not guess at the constraints line, field cardinality, or the URL history policy if they are still unclear.
2. **Plan:** Write the implementation plan covering the data migration, new files, filter logic, UI changes, and test strategy. **Stop and wait for my approval before changing any code.**
3. **Task tracking:** Once the plan is approved, create the tasks in **beads**: one epic for this feature, with child tasks for each work unit (taxonomy and reference tables, data migration, filter logic, URL state, UI, series pages, unit tests, Playwright tests). Record dependencies between tasks. Update task status as work progresses, and reference the task ID in commit messages.
4. **Implement:** Work through the tasks in the existing architecture, without rebuilding the site.
5. **Review:** Run unit and Playwright tests, then review your own diff against sections 6 and 7 before opening a PR. Report anything that deviates from the brief.
6. **Pull request:** Create the PR with a summary, linked beads tasks, test results, and any known limitations.
7. **Merge:** Ask me for approval to merge. Do not merge on your own.
