// Page editor: arrange a page's photos by hand, then save straight into the site folder (Chrome/Edge).
// The text edits live in pages-core.js; this file is the page and the file writing.
import { readWork, readLabels, writeLabels, editIndex, bumpLabels, editPhotos, photosJson, newId, cameraLine, readSelected, editSelected, selection } from './pages-core.js';

const $ = s => document.querySelector(s), tiles = $('.tiles');
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'})[c]);
// edits: page key -> working copy {p, cat, imgs, th, orig, touched}, 'selected' -> Selected work; added: new id -> its pictures and camera line
let WORK, labels, photos, picked, edits = new Map(), added = {}, dir = null, dirty = false;

async function load(){
  const get = f => fetch('../' + f, {cache: 'no-store'}).then(r => r.text()), keep = $('#page').value;
  const [html, lab, ph] = await Promise.all([get('index.html'), get('assets/home/labels.js'), get('data/photos.json')]);
  WORK = readWork(html); labels = readLabels(lab); photos = JSON.parse(ph); picked = selection(WORK, readSelected(html), photos);
  edits = new Map(); added = {}; dirty = false;
  $('#page').innerHTML = '<optgroup label="Home"><option value="selected">Selected work</option></optgroup>' + WORK.map(s => `<optgroup label="${esc(s.name)}">${s.projects.filter(p => !p.boulevard).flatMap(p => p.cats
    ? p.cats.map(c => `<option value="${s.id}|${p.id}|${esc(c.name)}">${esc(p.name)} · ${esc(c.name)}</option>`)
    : [`<option value="${s.id}|${p.id}|">${esc(p.name)}</option>`]).join('')}</optgroup>`).join('');
  if (keep) $('#page').value = keep;
}

// Selected work: an ordered list of photos from any page; × takes one out of it, nothing is deleted
const chosen = () => { if (!edits.has('selected')) edits.set('selected', {selected: true, p: {name: 'Selected work'}, imgs: [...picked], orig: [...picked], touched: false}); return edits.get('selected'); };

function page(){
  const k = $('#page').value;
  if (k === 'selected') return chosen();
  if (!edits.has(k)) {
    const [sid, pid, cat] = k.split('|'), p = WORK.find(s => s.id === sid).projects.find(x => x.id === pid);
    const imgs = cat ? p.cats.find(c => c.name === cat).imgs : p.imgs;
    edits.set(k, {p, cat: cat || undefined, imgs: [...imgs], th: p.th, orig: [...imgs], touched: false});
  }
  return edits.get(k);
}

const rec = id => photos.find(r => r.id === id);
const isFeatured = id => chosen().imgs.includes(id);
const src = id => added[id] ? added[id].url : rec(id) ? '../' + rec(id).thumb : `../assets/home/${id}.jpg`;

function draw(focus){
  const e = page(), photo = !e.p.poster && !e.selected, th = e.th || e.imgs[0];
  $('.add').hidden = !!e.selected;
  tiles.innerHTML = e.imgs.map((id, i) => `<li draggable="true" data-i="${i}" data-id="${esc(id)}"${added[id] ? ' class="new"' : ''}><img src="${esc(src(id))}" alt="" loading="lazy">
    <div class="meta"><b>${String(i + 1).padStart(2, '0')}</b><span>${esc(added[id] ? added[id].label || 'new · no camera line' : e.selected ? rec(id)?.alt : labels[id] || (photo ? 'no camera line' : ''))}</span></div>
    <div class="tools"><button data-a="left" aria-label="Move ${i + 1} earlier">←</button><button data-a="right" aria-label="Move ${i + 1} later">→</button>
    ${e.selected ? '' : `<button data-a="th" aria-pressed="${th === id}">menu</button>`}${photo && (rec(id) || added[id]) ? `<button data-a="star" aria-pressed="${isFeatured(id)}" aria-label="Featured">★</button>` : ''}
    <button class="x" data-a="x" aria-label="Remove ${i + 1}">×</button></div></li>`).join('');
  if (focus) tiles.querySelector(`li[data-i="${focus[0]}"] [data-a="${focus[1]}"]`)?.focus();
}

const change = focus => { page().touched = true; dirty = true; $('#status').textContent = 'unsaved changes'; draw(focus); };
const move = (from, to, a) => { const l = page().imgs; if (to < 0 || to >= l.length || from === to) return; l.splice(to, 0, l.splice(from, 1)[0]); change(a && [to, a]); };

tiles.addEventListener('click', ev => {
  const b = ev.target.closest('button'); if (!b) return;
  const i = +b.closest('li').dataset.i, e = page(), id = e.imgs[i];
  if (b.dataset.a === 'left' || b.dataset.a === 'right') return move(i, i + (b.dataset.a === 'left' ? -1 : 1), b.dataset.a);
  if (b.dataset.a === 'th') e.th = id;
  if (b.dataset.a === 'star') { const c = chosen(); c.imgs = c.imgs.includes(id) ? c.imgs.filter(x => x !== id) : [...c.imgs, id]; c.touched = true; }
  if (b.dataset.a === 'x') { e.imgs.splice(i, 1); if (e.th === id) e.th = undefined; }  // no menu photo: the menu shows the first one
  change([Math.min(i, e.imgs.length - 1), b.dataset.a === 'x' ? 'x' : b.dataset.a]);
});

let dragFrom = null;
tiles.addEventListener('dragstart', ev => { const li = ev.target.closest('li'); dragFrom = +li.dataset.i; li.classList.add('drag'); ev.dataTransfer.effectAllowed = 'move'; });
tiles.addEventListener('dragover', ev => {
  const li = ev.target.closest('li'); if (!li || dragFrom === null) return;
  ev.preventDefault(); tiles.querySelectorAll('.over').forEach(x => x.classList.remove('over')); li.classList.add('over');
});
tiles.addEventListener('drop', ev => { ev.preventDefault(); const li = ev.target.closest('li'); if (li && dragFrom !== null) move(dragFrom, +li.dataset.i); dragFrom = null; });
tiles.addEventListener('dragend', () => { dragFrom = null; draw(); });

// fits the picture inside w x h (never cropped) as a JPEG blob that knows its size
const jpeg = async (bmp, w, h = w) => {
  const k = Math.min(1, w / bmp.width, h / bmp.height), c = new OffscreenCanvas(Math.round(bmp.width * k), Math.round(bmp.height * k));
  c.getContext('2d').drawImage(bmp, 0, 0, c.width, c.height);
  return Object.assign(await c.convertToBlob({type: 'image/jpeg', quality: .82}), {w: c.width, h: c.height});
};

$('#files').addEventListener('change', async ev => {
  const e = page(), taken = new Set([...WORK.flatMap(s => s.projects.flatMap(p => p.imgs || (p.cats || []).flatMap(c => c.imgs))), ...Object.keys(labels), ...photos.map(r => r.id), ...Object.keys(added)]);
  $('#status').textContent = 'reading photos…';
  for (const f of ev.target.files) {
    const id = newId(e.p.id, f.name, taken), bmp = await createImageBitmap(f, {imageOrientation: 'from-image'}); taken.add(id);
    const big = await jpeg(bmp, 1600), cam = e.p.poster ? null : cameraLine(await f.arrayBuffer(), f.name);
    added[id] = {big, thumb: e.p.poster ? null : await jpeg(bmp, 600), url: URL.createObjectURL(big), label: cam?.label, date: cam?.date};
    e.imgs.push(id);
  }
  ev.target.value = ''; change();
});

const fail = msg => { $('#errors').textContent = msg; $('#status').textContent = ''; };

// where saves go: scripts/serve.py writes them (any browser), else a folder picked in Chrome/Edge
async function store(){
  if ((await fetch('/__can-save', {cache: 'no-store'}).catch(() => ({}))).status === 204) {
    const send = (p, method, body) => fetch('/' + p, {method, body, headers: {'X-Skimart-Save': '1'}}).then(r => { if (!r.ok) throw new Error(`${p}: ${r.status} ${r.statusText}`); });
    return {file: p => fetch('/' + p, {cache: 'no-store'}).then(r => { if (!r.ok) throw new Error(`${p}: ${r.status}`); return r.blob(); }),
      write: (p, data) => send(p, 'PUT', data), remove: p => send(p, 'DELETE').catch(() => {})};
  }
  if (!window.showDirectoryPicker) throw new Error('start the site with python3 scripts/serve.py to save (or use Chrome/Edge)');
  try { dir ||= await showDirectoryPicker({id: 'skimart-site', mode: 'readwrite'}); await dir.getFileHandle('index.html'); await dir.getDirectoryHandle('data'); }
  catch (err) { dir = null; throw err.name === 'AbortError' ? err : new Error('pick the site folder: the one that holds index.html'); }
  const at = async (p, create = false) => { const parts = p.split('/'), name = parts.pop(); let d = dir; for (const s of parts) d = await d.getDirectoryHandle(s, {create}); return [d, name]; };
  return {file: async p => { const [d, n] = await at(p); return (await d.getFileHandle(n)).getFile(); },
    write: async (p, data) => { const [d, n] = await at(p, true), w = await (await d.getFileHandle(n, {create: true})).createWritable(); await w.write(data); await w.close(); },
    remove: async p => { const [d, n] = await at(p).catch(() => []); await d?.removeEntry(n).catch(() => {}); }};
}

$('#save').addEventListener('click', async () => {
  $('#errors').textContent = '';
  let st;
  try { st = await store(); } catch (err) { if (err.name !== 'AbortError') fail('Not saved: ' + err.message); return; }
  $('#status').textContent = 'saving…';
  const {file, write} = st, has = p => file(p).then(() => true, () => false);
  try {
    // read the files as they are now on disk, so nothing saved since this page loaded is lost
    let html = await (await file('index.html')).text(), ph = JSON.parse(await (await file('data/photos.json')).text());
    const labJs = await (await file('assets/home/labels.js')).text(), lab = readLabels(labJs), pages = [...edits.values()].filter(e => e.touched && !e.selected);
    for (const e of pages) for (const id of e.imgs) if (added[id]) {
      await write(`assets/home/${id}.jpg`, added[id].big);
      if (added[id].thumb) await write(`assets/archive/t/${id}.jpg`, added[id].thumb);
      if (added[id].label) lab[id] = added[id].label;
    }
    for (const e of pages) html = editIndex(html, {proj: e.p.id, cat: e.cat, imgs: e.imgs, th: e.th === e.p.th ? undefined : e.th ?? null});
    // photos taken off a page and used nowhere else lose their caption, archive record and files
    const gone = pages.flatMap(e => e.orig.filter(id => !e.imgs.includes(id))).filter(id => !html.includes(`"${id}"`) && !html.includes(`'${id}'`));
    gone.forEach(id => delete lab[id]);
    for (const e of pages) if (!e.p.poster) ph = editPhotos(ph, {name: e.p.name, ids: e.imgs, removed: gone,
      added: Object.fromEntries(e.imgs.filter(id => added[id]?.thumb).map(id => [id, {w: added[id].thumb.w, h: added[id].thumb.h, date: added[id].date}]))});
    for (const e of pages) {  // the menu shows th, or the first photo: its small copy must exist
      const th = e.th || e.imgs[0];
      if (th && !(await has(`assets/home/t/${th}.jpg`))) await write(`assets/home/t/${th}.jpg`, await jpeg(await createImageBitmap(added[th]?.big || await file(`assets/home/${th}.jpg`)), 192, 120));
    }
    const c = chosen();
    if (gone.some(id => c.imgs.includes(id))) { c.imgs = c.imgs.filter(id => !gone.includes(id)); c.touched = true; }
    if (c.touched) {  // the order lives in index.html; the archive's featured flags follow it
      html = editSelected(html, c.imgs); const on = new Set(c.imgs); ph.forEach(r => { r.featured = on.has(r.id); });
    }
    const labText = writeLabels(labJs, lab);
    await write('assets/home/labels.js', labText); await write('data/photos.json', photosJson(ph)); await write('index.html', bumpLabels(html, labText));
    for (const id of gone) for (const p of [`assets/home/${id}.jpg`, `assets/home/t/${id}.jpg`, `assets/archive/t/${id}.jpg`]) await st.remove(p);
    await load(); draw(); $('#status').textContent = 'saved';
  } catch (err) { fail('Not saved: ' + err.message); }
});

addEventListener('beforeunload', ev => { if (dirty) ev.preventDefault(); });
$('#page').addEventListener('change', () => draw());
await load(); draw();
