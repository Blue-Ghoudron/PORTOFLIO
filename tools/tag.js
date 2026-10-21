// Tagging page: a contact sheet of every archive photo and a form that edits the selected ones together.
// Saves with the same formats the migration writes (photosJson / refsJson), and never saves data validate() rejects.
import { validate, slugify, photosJson, refsJson } from '../assets/archive/core.js';

const $ = s => document.querySelector(s), sheet = $('.sheet'), form = $('#form');
const LISTS = {location: 'locations', city: 'cities', client: 'clients', event: 'events', artist: 'artists'};
let data, sel = new Set(), dirty = false, dir = null;

const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'})[c]);
const chosen = () => data.photos.filter(p => sel.has(p.id));
const changed = () => { dirty = true; $('#status').textContent = 'unsaved changes'; drawSheet(); drawForm(); };

data = Object.fromEntries(await Promise.all(['taxonomy', 'refs', 'photos', 'series']
  .map(f => fetch(`../data/${f}.json`, {cache: 'no-store'}).then(r => r.json()).then(j => [f, j]))));
drawSheet(); drawForm();

function drawSheet(){
  const t = $('#find').value.toLowerCase(), only = $('#untagged').checked;
  sheet.innerHTML = data.photos.map(p => `<figure data-id="${p.id}" class="${sel.has(p.id) ? 'sel' : ''}"${(only && p.genres.length) || (t && !`${p.id} ${p.alt}`.toLowerCase().includes(t)) ? ' hidden' : ''}>
    <img src="../${encodeURI(p.thumb)}" alt="" loading="lazy"><figcaption>${esc(p.id)}<span>${p.genres.length || '–'}</span></figcaption></figure>`).join('');
}

// one value for all selected photos, or "mixed"
const same = get => { const v = chosen().map(p => JSON.stringify(get(p))); return v.every(x => x === v[0]) ? get(chosen()[0]) : undefined; };

function drawForm(){
  const ps = chosen();
  if (!ps.length) { form.innerHTML = '<p class="hint">Click a photo to edit it. Ctrl/Shift-click to edit several at once.</p>'; return; }
  const box = (name, id, label, key) => { const n = ps.filter(p => p[key].includes(id)).length;
    return `<label><input type="checkbox" name="${name}" value="${esc(id)}"${n === ps.length ? ' checked' : ''}${n && n < ps.length ? ' data-mixed' : ''}> ${esc(label)}</label>`; };
  const pick = (field, key) => { const v = same(p => p[key]);
    return `<label class="row">${field === 'location' ? 'place' : field}<select id="${field}"><option value="__mixed"${v === undefined ? ' selected' : ''} hidden>mixed</option><option value=""${v === null ? ' selected' : ''}>—</option>
      ${data.refs[LISTS[field]].map(r => `<option value="${esc(r.id)}"${v === r.id ? ' selected' : ''}>${esc(r.label)}</option>`).join('')}</select>
      <button type="button" class="new" data-list="${LISTS[field]}">new…</button></label>`; };
  const text = (id, key, tag = 'input') => { const v = same(p => p[key]);
    return tag === 'input' ? `<input id="${id}" value="${esc(v)}" placeholder="${v === undefined ? 'mixed' : ''}">` : `<textarea id="${id}" placeholder="${v === undefined ? 'mixed' : ''}">${esc(v)}</textarea>`; };
  const d = same(p => p.date), y = same(p => p.year), f = same(p => p.featured);
  form.innerHTML = `<h2>${ps.length === 1 ? esc(ps[0].id) : `${ps.length} photos`}</h2>
    ${ps.length === 1 ? `<img class="big" src="../${encodeURI(ps[0].thumb)}" alt="">` : ''}
    <fieldset><legend>genres</legend>${data.taxonomy.map(t => `<div class="grp"><b>${esc(t.label)}</b>${t.children.map(c => box('genre', c.id, c.label, 'genres')).join('')}</div>`).join('')}</fieldset>
    ${pick('location', 'locationId')}${pick('city', 'cityId')}
    <label class="row">date<input type="date" id="date" value="${d ?? ''}"${d === undefined ? ' placeholder="mixed"' : ''}></label>
    <label class="row">year<input type="number" id="year" value="${y ?? ''}" placeholder="${y === undefined ? 'mixed' : ''}" min="1900" max="2100"></label>
    <fieldset><legend>events <button type="button" class="new" data-list="events">new…</button></legend>${data.refs.events.map(e => box('event', e.id, e.label, 'eventIds')).join('')}</fieldset>
    <fieldset><legend>artists <button type="button" class="new" data-list="artists">new…</button></legend>${data.refs.artists.map(a => box('artist', a.id, a.label, 'artistIds')).join('')}</fieldset>
    ${pick('client', 'clientId')}
    <label class="row"><input type="checkbox" id="featured"${f ? ' checked' : ''}${f === undefined ? ' data-mixed' : ''}> featured</label>
    <label class="row">title${text('title', 'title')}</label>
    <label class="row">alt${text('alt', 'alt', 'textarea')}</label>`;
  form.querySelectorAll('[data-mixed]').forEach(i => i.indeterminate = true);
}

const ARR = {genre: 'genres', event: 'eventIds', artist: 'artistIds'};
const ONE = {location: 'locationId', city: 'cityId', client: 'clientId'};
form.addEventListener('change', e => {
  const t = e.target, ps = chosen();
  if (ARR[t.name]) for (const p of ps) { const a = p[ARR[t.name]].filter(x => x !== t.value); p[ARR[t.name]] = t.checked ? [...a, t.value] : a; }
  else if (ONE[t.id] && t.value !== '__mixed') for (const p of ps) p[ONE[t.id]] = t.value || null;
  else if (t.id === 'date') for (const p of ps) { p.date = t.value || null; if (t.value) p.year = +t.value.slice(0, 4); }
  else if (t.id === 'year') for (const p of ps) p.year = t.value ? +t.value : null;
  else if (t.id === 'featured') for (const p of ps) p.featured = t.checked;
  else if (t.id === 'title' || t.id === 'alt') for (const p of ps) p[t.id] = t.value || (t.id === 'title' ? null : '');
  else return;
  changed();
});

form.addEventListener('click', e => {
  const b = e.target.closest('button.new'); if (!b) return;
  const list = b.dataset.list, label = prompt(`New ${list.replace(/s$/, '').replace('citie', 'city').replace('location', 'place')}: name`)?.trim();
  if (!label) return;
  const id = slugify(label);
  if (!id || data.refs[list].some(r => r.id === id)) return alert(`"${id}" already exists`);
  const r = {id, label};
  if (list === 'locations') {  // a typed city name becomes its id, and a city the data doesn't know yet is added
    const c = prompt(`City of ${label} (${data.refs.cities.map(c => c.label).join(', ')})`, 'Casablanca')?.trim();
    if (c) { r.cityId = slugify(c); if (!data.refs.cities.some(x => x.id === r.cityId)) data.refs.cities.push({id: r.cityId, label: c}); }
  }
  if (list === 'events') { const y = prompt(`Year of ${label}`); if (y) r.year = +y; }
  data.refs[list].push(r);
  // the new entry goes straight onto the selected photos
  const key = {events: 'eventIds', artists: 'artistIds'}[list] || {locations: 'locationId', cities: 'cityId', clients: 'clientId'}[list];
  for (const p of chosen()) Array.isArray(p[key]) ? p[key].push(id) : p[key] = id;
  changed();
});

sheet.addEventListener('click', e => {
  const f = e.target.closest('figure'); if (!f) return;
  if (e.ctrlKey || e.metaKey || e.shiftKey) sel.has(f.dataset.id) ? sel.delete(f.dataset.id) : sel.add(f.dataset.id);
  else sel = new Set([f.dataset.id]);
  drawSheet(); drawForm();
});
$('#untagged').onchange = drawSheet;
$('#find').oninput = drawSheet;

$('#save').onclick = async () => {
  const errors = validate(data);
  $('#errors').innerHTML = errors.map(x => `<p>${esc(x)}</p>`).join('');
  if (errors.length) return;
  const files = {'photos.json': photosJson(data.photos), 'refs.json': refsJson(data.refs)};
  if (window.showDirectoryPicker) {
    // only write into the archive's data/ folder: it is the one that already holds taxonomy.json
    try { dir ||= await showDirectoryPicker({id: 'skimart-data', mode: 'readwrite'}); await dir.getFileHandle('taxonomy.json'); }
    catch (err) {
      dir = null;
      if (err.name === 'AbortError') { $('#status').textContent = 'not saved'; return; }
      $('#errors').innerHTML = '<p>That folder is not the archive data: pick the repo\'s data/ folder (the one with taxonomy.json).</p>'; return;
    }
    for (const [name, text] of Object.entries(files)) { const w = await (await dir.getFileHandle(name, {create: true})).createWritable(); await w.write(text); await w.close(); }
  } else for (const [name, text] of Object.entries(files)) {
    const a = Object.assign(document.createElement('a'), {href: URL.createObjectURL(new Blob([text], {type: 'application/json'})), download: name});
    a.click(); URL.revokeObjectURL(a.href);
  }
  dirty = false; $('#status').textContent = window.showDirectoryPicker ? 'saved' : 'downloaded: put both files in data/';
};
addEventListener('beforeunload', e => { if (dirty) e.preventDefault(); });
