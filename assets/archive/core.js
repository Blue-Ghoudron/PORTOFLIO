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
  // genres are the way in, so they count the whole archive; picking one then drops what no longer fits (changeGenre)
  const count = ids => photos.filter(p => (p.genres || []).some(g => ids.includes(g))).length;
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

export const slugify = s => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
  .replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

const KEYS = ['genre', ...FIELDS];
const allowed = (field, data) => field === 'year'
  ? new Set(data.photos.filter(p => p.year != null).map(p => String(p.year)))
  : new Set((data.refs[REF[field]] || []).map(x => x.id));

// query is the part after "?" in #photography/archive?…; anything unknown is dropped, never thrown
export function parseQuery(query, data){
  const s = emptyState();
  let q; try { q = new URLSearchParams(query); } catch (e) { return s; }
  const g = q.get('genre');
  if (g && data.taxonomy.some(t => t.id === g || t.children.some(c => c.id === g))) s.genre = g;
  for (const f of FIELDS) {
    const ok = allowed(f, data);
    s[f] = [...new Set((q.get(f) || '').split(',').filter(v => ok.has(v)))];
  }
  return s;
}

export const serializeQuery = state => KEYS
  .filter(k => k === 'genre' ? state.genre : state[k].length)
  .map(k => `${k}=${k === 'genre' ? state.genre : state[k].join(',')}`).join('&');

export function validate(data){
  const err = [], seen = new Set(), refs = data.refs || {};
  const has = (list, id) => (refs[list] || []).some(x => x.id === id);
  const leafIds = new Set(data.taxonomy.flatMap(t => t.children.map(c => c.id)));
  for (const l of refs.locations || []) if (l.cityId && !has('cities', l.cityId)) err.push(`location ${l.id}: unknown city "${l.cityId}"`);
  for (const p of data.photos) {
    if (seen.has(p.id)) err.push(`duplicate id ${p.id}`); seen.add(p.id);
    for (const g of p.genres || []) if (!leafIds.has(g)) err.push(`photo ${p.id}: unknown genre "${g}"`);
    const one = (field, list, id) => id != null && !has(list, id) && err.push(`photo ${p.id}: unknown ${field} "${id}"`);
    one('location', 'locations', p.locationId); one('city', 'cities', p.cityId); one('client', 'clients', p.clientId);
    for (const e of p.eventIds || []) one('event', 'events', e);
    for (const a of p.artistIds || []) one('artist', 'artists', a);
  }
  for (const s of data.series || []) for (const id of s.photoIds) if (!seen.has(id)) err.push(`series ${s.id}: unknown photo ${id}`);
  return err;
}

// the on-disk formats: one photo per line keeps git diffs readable; the migration and the tagging page both write these
export const photosJson = photos => '[\n' + photos.map(p => JSON.stringify(p)).join(',\n') + '\n]\n';
export const refsJson = refs => JSON.stringify(refs, null, 1) + '\n';
