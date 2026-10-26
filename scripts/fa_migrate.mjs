// Builds the archive data (data/refs.json, photos.json, series.json) from facts the site already states:
// the WORK info lines in index.html and the captions of the L'Boulevard rooms. Never overwrites a record
// that already exists, so it is safe to re-run after tagging (it only appends photos that are missing).
//   node scripts/fa_migrate.mjs            then make thumbnails:
//   ~/.cache/orbit-render/v/bin/python -I scripts/fa_thumbs.py
// FA_DATA=<dir> writes somewhere else (the unit test uses it).
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { slugify, validate, photosJson, refsJson } from '../assets/archive/core.js';

const DATA = process.env.FA_DATA || 'data';

const ref = (label, extra = {}) => ({id: slugify(label), label, ...extra});
const AAC = 'american-arts-center';
const REFS = {
  cities: [ref('Casablanca')],
  locations: [ref('Technopark · Sidi Maarouf', {cityId: 'casablanca'}), ref('Seamens Club', {cityId: 'casablanca'}), ref('American Arts Center', {cityId: 'casablanca'})],
  events: [ref('Jazz', {year: 2025, date: '2025-05-16'}), ref('Summer Sessions', {year: 2026, date: '2026-08-22'}),
    ref('Noches de Ramadán', {year: 2026, date: '2026-02-24'}), ref('Poster Making workshop', {year: 2026, date: '2026-02-13'}),
    ref("L'Boulevard 2025", {year: 2025, date: '2025-09-20'}), ref("L'Boulevard 2026", {year: 2026, date: '2026-09-19'})],
  artists: ['Mehdi Ainak', 'Hellboy', 'Ayoub Hattab', 'Jamila & the Other Heroes', 'Nanofunk', 'Disco Atlas', 'Pagan Ulver', 'Suicide Machine'].map(a => ref(a)),
  clients: [],
};

// only what each project's info line or title says (spec: "Filling the data")
const FACTS = {
  'technopark': {locationId: 'technopark-sidi-maarouf'},
  'hellboy-mehdi': {date: '2025-06-27', artistIds: ['mehdi-ainak', 'hellboy']},
  'summer-sessions': {locationId: 'seamens-club', date: '2026-08-22', eventIds: ['summer-sessions']},
  'ayoub-hattab': {locationId: AAC, date: '2025-06-13', artistIds: ['ayoub-hattab']},
  'jamila': {locationId: AAC, date: '2025-11-22', artistIds: ['jamila-the-other-heroes']},
  'jazz': {locationId: AAC, date: '2025-05-16', eventIds: ['jazz']},
  'nanofunk': {locationId: AAC, date: '2025-07-28', artistIds: ['nanofunk']},
  'disco-atlas': {locationId: AAC, date: '2025-06-26', artistIds: ['disco-atlas']},
  'noches': {locationId: AAC, date: '2026-02-24', eventIds: ['noches-de-ramadan']},
  'poster-making': {locationId: AAC, date: '2026-02-13', eventIds: ['poster-making-workshop']},
};
const ROOMS = [['Band', 'connection', 'Connection'], ['Movement', 'movement', 'Movement'], ['Faces', 'faces-and-eyes', 'Faces and Eyes']];
const BANDS = ['Pagan Ulver', 'Suicide Machine'];

const record = (id, title, image, f, alt) => ({id, title, image, thumb: `assets/archive/t/${id}.jpg`, w: null, h: null,
  discipline: 'photography', genres: [], locationId: f.locationId ?? null, cityId: f.cityId ?? null,
  year: f.date ? +f.date.slice(0, 4) : null, date: f.date ?? null, eventIds: f.eventIds ?? [], artistIds: f.artistIds ?? [],
  clientId: null, featured: false, alt});

const html = readFileSync('index.html', 'utf8'), start = html.indexOf('const WORK = ') + 13;
const WORK = new Function('return ' + html.slice(start, html.indexOf('];\n', start) + 1))();
const fresh = [];
for (const sec of WORK) for (const p of sec.projects) if (FACTS[p.id])
  p.imgs.forEach((img, i) => fresh.push(record(img, null, `assets/home/${img}.jpg`, FACTS[p.id], `${p.name}, photo ${i + 1}`)));

const decode = s => s.replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');
const series = ROOMS.map(([dir, id, title]) => {
  const page = readFileSync(`assets/boulevard/${dir}/index.html`, 'utf8'), photoIds = [];
  for (const [, cap, file, alt] of page.matchAll(/<button class="shot"[^>]*data-cap="([^"]*)"[^>]*><img src="images\/([^"]+)" alt="([^"]*)"/g)) {
    const parts = decode(cap).split(' · '), year = parts.find(x => /^20\d\d$/.test(x)), pid = `lbv-${dir.toLowerCase()}-${file.replace(/\.\w+$/, '')}`;
    fresh.push(record(pid, /^\d+$/.test(parts[0]) ? parts[1] : null, `assets/boulevard/${dir}/images/${file}`, {
      cityId: 'casablanca', date: {2025: '2025-09-20', 2026: '2026-09-19'}[year], eventIds: [`l-boulevard-${year}`],
      artistIds: BANDS.filter(b => cap.includes(b)).map(slugify)}, decode(alt)));
    photoIds.push(pid);
  }
  return {id, title, href: `#photography/boulevard/${dir}`, photoIds};
});

const read = (f, empty) => existsSync(join(DATA, f)) ? JSON.parse(readFileSync(join(DATA, f), 'utf8')) : empty;
const photos = read('photos.json', []), have = new Set(photos.map(p => p.id));
photos.push(...fresh.filter(p => !have.has(p.id)));
const refs = read('refs.json', {});
for (const k of Object.keys(REFS)) { refs[k] ||= []; for (const r of REFS[k]) if (!refs[k].some(x => x.id === r.id)) refs[k].push(r); }

const data = {taxonomy: read('taxonomy.json', []), refs, photos, series}, errors = validate(data);
if (errors.length) { console.error(errors.join('\n')); process.exit(1); }
writeFileSync(join(DATA, 'photos.json'), photosJson(photos));
writeFileSync(join(DATA, 'refs.json'), refsJson(refs));
writeFileSync(join(DATA, 'series.json'), JSON.stringify(series, null, 1) + '\n');
console.log(`${photos.length} photos (${photos.length - have.size} new), ${series.length} series`);
