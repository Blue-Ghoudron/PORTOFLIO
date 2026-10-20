# Faces and Eyes — tasks

Page: `Faces/index.html` on `Faces-and-Eyes-Branch` (local preview: http://localhost:8000/Faces/).
Status (20.10.2026): built with 34 photos (10 hung, 4 in the 17-second strip, 20 in the gallery). Checked with Playwright, committed and pushed, PR open.

## 1. From you

- [x] **Concept:** title "Faces and Eyes". The rooms follow what the eyes do: they look back, they are covered, they are painted.
- [x] **Photos:** `Boulevard_20.09.2025/Lightroom/Portrait` and `Boulevard_20.09.2026/Boulevard_26.jpg/Lightroom/Portrait`, both years.
- [x] **Branch:** Movement committed on `Movement-Branch` (not pushed), `Faces-and-Eyes-Branch` made from it.
- [x] **Instagram posts:** read through the public embed. DeSVtD7kUiS is "FACES / YOU CAN HEAR THEM LOUD / L'Boulvard 2025" and DeprHrWDb3P is "EYES / DEATH AND THRASH / L'Boulvard, Casablanca - 2026". They name the gallery's two walls. Photo tags need a login, so I couldn't read them.
- [x] **Tagging sitters (20.10.2026, you said "all"):** 31 photos carry their sitter's Instagram (handle from the `people/` folder name) under the title, next to the number in the strip and gallery, and at the end of the viewer caption. Not tagged: G04, G05 (no handle folder), G10 (folder is a phone number, never on the page).

## 2. Curation (approved 20.10.2026)

| # | Room | Photo | Title (proposal) |
|---|---|---|---|
| 01 | Prologue | IMG_9304 · 2025 · 20:49:00 | One eye lit |
| 02 | I Looking back | IMG_9146 · 2025 · 18:47:21 | Sign of the horns |
| 03 | | IMG_9293 · 2025 · 20:45:43 | Held stare |
| 04 | | IMG_0496 · 2026 · 22:17:09 | Over the shoulder |
| 05 | II Covered | IMG_9295 · 2025 · 20:46:01 | Hand over the eye |
| 06 | | IMG_0547 · 2026 · 22:49:25 | Spikes |
| 07 | | IMG_0586 · 2026 · 23:20:33 | Veil |
| 08 | III Painted | IMG_9362 · 2025 · 21:53:45 | White eyes |
| 09 | | IMG_0527 · 2026 · 22:36:53 | Tongue |
| 10 | | IMG_0570 · 2026 · 22:57:35 | The line |
| F1–F4 | 17 seconds | IMG_0544 → 0545 → 0546 → 0548 · 2026 · 22:49:13–22:49:30 (+0, +3, +7, +17 s) | |

- [x] Inventory and contact sheets of both Portrait folders.
- [x] Proposal with rooms, exclusions and titles.
- [x] **You approved** the selection and order.

Left out: 9287, 9297, 9298 (already on Connection, and they're stage shots). Crowd or stage frames, not portraits: 9238, 9249, 9279, 0263, 0265, 0389, 0554. Group shots: 9410, 0368, 0418, 0528, 0533, 0551, 0571. Near-duplicates: 9296, 9363, 0489, 0591, 0572. Cut to keep the count down (any can swap in): 9169, 9322, 9331, 9343, 9344, 9345, 9346, 9373, 9414, 0357, 0380, 0393, 0409, 0446, 0477, 0488, 0492, 0564, 0590, 0594.

## 3. Build

- [x] Web copies (`fac-*.jpg`, 1882 px wide with the #EEFFE5 mat, camera data copied from the originals).
- [x] Page from Movement's template: hero with the portrait prologue, three rooms of three portraits stepping down the wall, the 17-second strip, outro ("Blink"), footer.
- [x] Statement (~75 words), subtitle "Close to the lens", camera line (2025: EF 50mm f/1.8 STM, 02 on the EF-S 18–55mm. 2026: EF 50mm f/1.4 USM).
- [x] "Faces and Eyes" link added to the page switch on Connection and Movement.

- [x] **Gallery (20.10.2026, your request):** 20 more portraits in two walls. Faces · 2025: 9169, 9322, 9331, 9343, 9344, 9345, 9346, 9373, 9414. Eyes · 2026: 0357, 0380, 0393, 0409, 0446, 0477, 0488, 0492, 0564, 0590, 0594. Numbered G01–G20, open in the viewer, #G01 links work.
- [x] **Hero (your note on the empty middle):** the title is now two lines (FACES / AND EYES) and reaches the photo. Byline, statement and route sit under it, beside the photo.

## 4. Check and ship

- [x] Playwright check at phone, tablet, 1366×768 and 1862×952: no errors, no sideways scroll, all photos load, viewer opens, steps and closes, #07/#F4 links work, nav works both ways on all three pages.
- [x] Commit on `Faces-and-Eyes-Branch`, push, open a PR into `main`.
- [ ] Merge, only when you say so. The PR also carries the Movement commit, because this branch was made from it.
- [ ] Publish: a new artifact, or an existing link? **Your call.**

## 5. Open

- [ ] **Titles** (One eye lit, Sign of the horns, Held stare, Over the shoulder, Hand over the eye, Spikes, Veil, White eyes, Tongue, The line), the subtitle and the outro word are proposals. Rename freely.
- [ ] Check the tags are right: they come from your folder names, not from the Instagram posts (photo tags need a login to read).

## Swaps and stacks (20.10.2026)
- [x] Hung ↔ gallery swaps (your call): 03 ← IMG_0393 "Hood" · 04 ← IMG_9344 "Chin up" · 09 ← IMG_0357 "Smoke". 9293, 0496 and 0527 moved to the gallery in time order.
- [x] Two vertical stacks in the gallery, made like the GRID exports (`~/.cache/lbv-faces2/stack.py`): G01 = 2025 Groups 9158 / 9148 / 9315 (your Instagram slide), G19 = 2026 0545 / 0571 (GRID/Portrait P4). All five frames tagged from their `people/` folders. Gallery is now G01–G22.
- [ ] Room III "Painted" now holds 0357 (sunglasses and smoke, no paint); its line was widened to "dark glasses". 0545 is both F2 in "17 seconds" and in the G19 stack.
