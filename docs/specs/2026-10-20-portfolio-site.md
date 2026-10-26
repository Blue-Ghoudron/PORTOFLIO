# SKIMART portfolio site — spec

Status: built on `Portoflio-Branch` (PR #2 to `main`, not merged). Written 20.10.2026 from what was decided and shipped.

## Why
One place that shows Ghoujlami Mohamed (SKIMART) as a **photographer first**, with graphic design as a second strength. People who could hire or collaborate (venues, festivals, cultural spaces) should see real photos within a second and have a clear way to make contact. Source brief: `Homepage Implementation Brief.txt`.

## Goals
- The first screen is a real photograph, with "Photographer / Visual Artist" and "Real moments. Visual stories."
- Every project is two clicks away from the side menu: Photography (Street, Clubs, American Arts Center, L'Boulevard), Design (posters), Workshops.
- L'Boulevard is presented as an **exhibition** inside the portfolio, keeping its own look.
- Works on phones; light and dark themes; photos can be seen full screen.

## Non-goals
- No CMS, no build tool, no framework: plain static files.
- No blog, shop or contact form; contact is email and Instagram.

## Anti-goals (a failure even if it works)
- Invented project descriptions, clients, awards or credits.
- Generic template look: rounded cards, gradients, stock images.
- L'Boulevard losing its plum / cream / blue identity or its matted prints.

## Decisions (the user's)
| Question | Decision |
|---|---|
| Navigation | Side menu with folding sections (v4 mockup), burger menu on phones |
| Home vs About | Separate: Home = hero + two lines; About = its own view (`#about`) |
| L'Boulevard | Opens inside the portfolio in an iframe; the portfolio takes the exhibition palette and follows its theme switch. (First built as links to separate pages, then changed in the "Pages" session; the user approved the iframe version for PR #2.) |
| Branches | Fixes on `Portoflio-Fixes` |

## How it works
See `CLAUDE.md` › Architecture. In short: `index.html` is a hash router over the `WORK` array; photos are in `assets/home/`; the exhibition is in `assets/boulevard/`.

## Open
- About bio: placeholder until the user sends the text.
- Known bugs from the review of PR #2: a room is not kept in the address (refresh goes back to the hub), and keyboard focus escapes the photo viewer. Tracked as `pf-qsm.2` and `pf-qsm.5`.
- Unused code and files: `doors` data, `.list .sub/.ext` CSS, `assets/home/b-*.jpg`.
- Not published yet (GitHub Pages is off).
