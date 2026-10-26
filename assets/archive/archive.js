// Archive view (#photography/archive): filters above the photos (spec, layout A). The filter logic is in core.js;
// this file only draws it and keeps the address in step. index.html's router calls showArchive().
import { FIELDS, emptyState, applyFilters, computeOptions, changeGenre, parseQuery, serializeQuery, validate } from './core.js';

const NAMES = {location: 'place', city: 'city', year: 'year', event: 'event', artist: 'artist', client: 'client'};
const REF = {location: 'locations', city: 'cities', event: 'events', artist: 'artists', client: 'clients'};
let data = null, from = null, state = emptyState(), view = null, settle = () => {}, openDd = null, drawer = false, tools = '';

export const load = () => data ||= Promise.all(['taxonomy', 'refs', 'photos', 'series'].map(f => fetch(`data/${f}.json`).then(r => r.json())))
  .then(([taxonomy, refs, photos, series]) => {
    const d = {taxonomy, refs, photos, series}, errors = validate(d);
    if (errors.length) console.warn('archive data:\n' + errors.join('\n'));
    return d;
  });

const esc = s => String(s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'})[c]);
const label = (d, f, id) => f === 'year' ? id : (d.refs[REF[f]] || []).find(x => x.id === id)?.label ?? id;
const genreLabel = (d, id) => d.taxonomy.flatMap(t => [t, ...t.children]).find(g => g.id === id)?.label ?? id;
const when = p => p.date ? p.date.split('-').reverse().join('.') : p.year ?? '';

// where each photo comes from: its homepage project, else its L'Boulevard room
function origins(d, work){
  const m = new Map();
  for (const s of d.series) for (const id of s.photoIds) m.set(id, {label: s.title, href: s.href});
  for (const sec of work) for (const p of sec.projects) for (const id of p.imgs || []) m.set(id, {label: p.name, href: `#${sec.id}/${p.id}`});
  return m;
}

export async function showArchive(v, query, work, after, layout = ''){
  view = v; settle = after || settle; tools = layout;
  const d = await load();
  if (!location.hash.startsWith('#photography/archive')) return;  // the visitor left while the data was loading
  from ||= origins(d, work);
  state = parseQuery(query, d);
  draw(d);
}

function draw(d){
  const o = computeOptions(d.photos, state, d), shown = applyFilters(d.photos, state, d);
  const parent = o.genres.find(g => g.id === state.genre || g.children.some(c => c.id === state.genre));
  const pressed = on => `aria-pressed="${on}"`;
  const genres = o.genres.length ? `<nav class="fa-genres mono" aria-label="Genre">
      <button data-genre="" ${pressed(!state.genre)}>All</button>${o.genres.map(g => `<button data-genre="${g.id}" ${pressed(g === parent)}>${esc(g.label)}</button>`).join('')}</nav>
    ${parent ? `<div class="fa-sub mono">${parent.children.map(c => `<button data-genre="${c.id}" ${pressed(c.id === state.genre)}>${esc(c.label.toLowerCase())} <span class="n">(${c.count})</span></button>`).join('')}</div>` : ''}` : '';
  const dds = FIELDS.filter(f => o.groups[f]).map(f => {
    const sel = state[f], opts = o.groups[f];
    const sum = sel.length === 1 ? `${NAMES[f]}: <b>${esc(label(d, f, sel[0]))}</b>` : sel.length ? `${NAMES[f]}: <b>${sel.length}</b>` : NAMES[f];
    return `<details class="fa-dd" data-field="${f}"${openDd === f ? ' open' : ''}><summary>${sum} <span aria-hidden="true">▾</span></summary>
      <div class="fa-menu" role="group" aria-label="${NAMES[f]}">${opts.length > 8 ? `<input type="search" placeholder="search ${NAMES[f]}" aria-label="Search ${NAMES[f]}">` : ''}
      ${opts.map(x => `<label><input type="checkbox" value="${esc(x.id)}"${sel.includes(x.id) ? ' checked' : ''}> <span class="l">${esc(x.label)}</span> <span class="n">(${x.count})</span></label>`).join('')}</div></details>`;
  }).join('');
  const chips = [...(state.genre ? [['genre', state.genre, genreLabel(d, state.genre)]] : []),
    ...FIELDS.flatMap(f => state[f].map(v => [f, v, label(d, f, v)]))];
  const n = shown.length;
  // the visible count is redrawn with everything else; screen readers hear this one region, which stays put
  const live = document.getElementById('fa-live') || document.body.appendChild(Object.assign(document.createElement('p'), {id: 'fa-live', className: 'fa-sr'}));
  live.setAttribute('aria-live', 'polite'); live.textContent = `${n} photograph${n === 1 ? '' : 's'}`;
  view.innerHTML = `<section class="proj archive"><h2 tabindex="-1">Archive</h2><p class="info">Every photograph · filter by genre, place, year, event</p>${tools}
    <button class="fa-open mono" aria-expanded="${drawer}" aria-controls="fa-panel">Filter</button>
    <div class="fa-panel${drawer ? ' open' : ''}" id="fa-panel">${genres}${dds ? `<div class="fa-dds mono">${dds}</div>` : ''}
      <button class="fa-done mono">show ${n} photograph${n === 1 ? '' : 's'}</button></div>
    <div class="fa-chips mono">${chips.map(([f, v, l]) => `<button class="fa-chip" data-field="${f}" data-value="${esc(v)}" aria-label="Remove ${esc(l)}">${esc(l)} ×</button>`).join('')}
      ${chips.length ? '<button class="fa-clear">clear all</button>' : ''}<p class="fa-count">${n} photograph${n === 1 ? '' : 's'}</p></div>
    ${n ? `<div class="grid fa-grid">${shown.map((p, i) => {
      const src = from.get(p.id), cap = [src?.label, when(p)].filter(Boolean).join(' · ');
      return `<figure data-zoom data-id="${p.id}" data-cam="${esc(cap)}"${src ? ` data-from-href="${src.href}" data-from-label="${esc(src.label)}"` : ''}${p.image.startsWith('assets/boulevard/') ? ' data-mat' : ''} tabindex="0" role="button" aria-label="Enlarge photo ${i + 1}">
        <img src="${encodeURI(p.thumb)}" data-full="${encodeURI(p.image)}" width="${p.w}" height="${p.h}" alt="${esc(p.alt)}" loading="lazy"><figcaption><span class="cam">${esc(cap)}</span></figcaption></figure>`;
    }).join('')}</div>` : '<div class="fa-empty"><p>No photographs match.</p><button class="fa-reset">reset filters</button></div>'}</section>`;
  settle();
}

// a genre change is a step Back can return to; ticking a box only rewrites the current address
function commit(next, focus){
  const push = next.genre !== state.genre, q = serializeQuery(next);
  state = next;
  history[push ? 'pushState' : 'replaceState'](null, '', '#photography/archive' + (q ? '?' + q : ''));
  // focus goes to the first of the given places that still exists after the redraw, never to <body>
  data.then(d => { draw(d); (focus + '|.archive h2').split('|').map(f => view.querySelector(f)).find(Boolean).focus(); });
}

const onArchive = e => e.target.closest('.archive');
// an open dropdown closes on a click elsewhere or on Escape, like a native select
const closeDds = keep => document.querySelectorAll('.fa-dd[open]').forEach(d => d.contains(keep) || (d.open = false, openDd = null));
addEventListener('keydown', e => {
  if (e.key !== 'Escape') return;
  const d = e.target.closest?.('.fa-dd[open]');
  if (d) { d.open = false; d.querySelector('summary').focus(); } else if (drawer && e.target.closest?.('#fa-panel')) setDrawer(false);
});
// phones: the filters sit in a full-screen drawer; on wider screens the button and the drawer styling are hidden by CSS
function setDrawer(open){
  drawer = open;
  view.querySelector('#fa-panel').classList.toggle('open', open);
  const b = view.querySelector('.fa-open'); b.setAttribute('aria-expanded', open);
  (open ? view.querySelector('#fa-panel button, #fa-panel summary') : b)?.focus();
}
addEventListener('click', e => {
  closeDds(e.target);
  if (!onArchive(e)) return;
  const g = e.target.closest('[data-genre]'), chip = e.target.closest('.fa-chip');
  if (g) data.then(d => commit(changeGenre(state, g.dataset.genre, d.photos, d), `[data-genre="${g.dataset.genre}"]`));
  else if (chip) data.then(d => {
    const {field, value} = chip.dataset;
    commit(field === 'genre' ? changeGenre(state, null, d.photos, d) : {...state, [field]: state[field].filter(v => v !== value)}, '.fa-chip|[data-genre=""]|.fa-dd summary');
  });
  else if (e.target.closest('.fa-clear, .fa-reset')) commit(emptyState(), '[data-genre=""]|.fa-dd summary');
  else if (e.target.closest('.fa-open, .fa-done')) setDrawer(!!e.target.closest('.fa-open'));
});
addEventListener('change', e => {
  const box = e.target.closest('.fa-dd input[type=checkbox]');
  if (!box || !onArchive(e)) return;
  const f = box.closest('.fa-dd').dataset.field, v = box.value;
  openDd = f;
  commit({...state, [f]: box.checked ? [...state[f], v] : state[f].filter(x => x !== v)}, `.fa-dd[data-field="${f}"] input[value="${CSS.escape(v)}"]`);
});
addEventListener('toggle', e => { const dd = e.target.closest?.('.fa-dd'); if (dd) openDd = dd.open ? dd.dataset.field : openDd === dd.dataset.field ? null : openDd; }, true);
addEventListener('input', e => {
  if (!e.target.matches('.fa-menu input[type=search]')) return;
  const t = e.target.value.toLowerCase();
  e.target.closest('.fa-menu').querySelectorAll('label').forEach(l => l.hidden = !l.textContent.toLowerCase().includes(t));
});
