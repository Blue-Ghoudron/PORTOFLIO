// Archive filter logic: pure functions, no DOM, so node --test can run them (tests/fa_core.test.mjs).
// data = {taxonomy, refs, photos, series}, as in data/*.json. A state holds slugs only; years as strings.

export const FIELDS = ['location', 'city', 'year', 'event', 'artist', 'client'];
const REF = {location: 'locations', city: 'cities', event: 'events', artist: 'artists', client: 'clients'};

export const emptyState = () => ({genre: null, location: [], city: [], year: [], event: [], artist: [], client: []});

export function leaves(taxonomy, genreId){
  for (const g of taxonomy) {
    if (g.id === genreId) return g.children.map(c => c.id);
    if (g.children.some(c => c.id === genreId)) return [genreId];
  }
  return [];
}

const byId = (list, id) => (list || []).find(x => x.id === id);

export function valuesOf(photo, field, refs){
  const v = {
    location: [photo.locationId],
    city: [photo.cityId ?? byId(refs.locations, photo.locationId)?.cityId],
    year: [photo.year == null ? null : String(photo.year)],
    event: photo.eventIds || [],
    artist: photo.artistIds || [],
    client: [photo.clientId],
  }[field];
  return v.filter(x => x != null);
}

// every filter except `skip` (a field, or 'genre'), so options can be counted against the others
function matches(photo, state, data, skip){
  if (skip !== 'genre' && state.genre) {
    const ls = leaves(data.taxonomy, state.genre);
    if (!(photo.genres || []).some(g => ls.includes(g))) return false;
  }
  return FIELDS.every(f => f === skip || !state[f].length || valuesOf(photo, f, data.refs).some(v => state[f].includes(v)));
}

export const sortPhotos = photos => [...photos].sort((a, b) =>
  (a.date && b.date ? b.date.localeCompare(a.date) : a.date ? -1 : b.date ? 1 : 0) || a.id.localeCompare(b.id));

export const applyFilters = (photos, state, data) => sortPhotos(photos.filter(p => matches(p, state, data)));

const label = (field, id, refs) => field === 'year' ? id : byId(refs[REF[field]], id)?.label ?? id;

export function computeOptions(photos, state, data){
  const groups = {};
  for (const f of FIELDS) {
    const n = new Map();
    for (const p of photos) if (matches(p, state, data, f)) for (const v of new Set(valuesOf(p, f, data.refs))) n.set(v, (n.get(v) || 0) + 1);
    const opts = [...n].map(([id, count]) => ({id, label: label(f, id, data.refs), count}))
      .sort((a, b) => a.label.localeCompare(b.label));
    // a single choice filters nothing, unless it is already selected
    if (opts.length > 1 || state[f].length) groups[f] = opts;
  }
  const pool = photos.filter(p => matches(p, state, data, 'genre'));
  const count = ids => pool.filter(p => (p.genres || []).some(g => ids.includes(g))).length;
  const genres = data.taxonomy.map(g => ({id: g.id, label: g.label, count: count(g.children.map(c => c.id)),
    children: g.children.map(c => ({id: c.id, label: c.label, count: count([c.id])})).filter(c => c.count)}))
    .filter(g => g.count);
  return {genres, groups};
}

// keep each selected value only while the new genre plus everything kept so far still finds a photo
export function changeGenre(state, genreId, photos, data){
  const next = {...emptyState(), genre: genreId || null};
  for (const f of FIELDS) for (const v of state[f])
    if (photos.some(p => matches(p, {...next, [f]: [v]}, data))) next[f] = [...next[f], v];
  return next;
}

export const slugify = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
  .replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
