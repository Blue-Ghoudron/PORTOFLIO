// Page editor text edits (tools/pages-core.js), on the real index.html / labels.js where it can.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { readWork, readLabels, writeLabels, editIndex, bumpLabels, editPhotos, newId, cameraLine, readSelected, editSelected, selection, insertProject, orderProjects } from '../tools/pages-core.js';

const ROOT = fileURLToPath(new URL('..', import.meta.url));
const html = readFileSync(join(ROOT, 'index.html'), 'utf8'), labelsJs = readFileSync(join(ROOT, 'assets/home/labels.js'), 'utf8');
const proj = (w, id) => w.flatMap(s => s.projects).find(p => p.id === id);

test('reorder and menu photo round-trip through index.html', () => {
  const s = proj(readWork(html), 'soualem'), imgs = [...s.imgs].reverse();
  const w = readWork(editIndex(html, {proj: 'soualem', imgs, th: imgs[0]}));
  assert.deepEqual(proj(w, 'soualem').imgs, imgs); assert.equal(proj(w, 'soualem').th, imgs[0]);
  assert.deepEqual(proj(w, 'jazz').imgs, proj(readWork(html), 'jazz').imgs);  // other pages untouched
});

test('menu photo added to a page that had none', () => {
  const j = readWork(html)[0].projects.find(p => p.imgs?.length > 2 && !p.th);  // any page still without one
  assert.equal(proj(readWork(editIndex(html, {proj: j.id, imgs: j.imgs, th: j.imgs[2]})), j.id).th, j.imgs[2]);
});

test('dropping the menu photo falls back to the first photo', () => {
  const s = proj(readWork(html), 'soualem');
  assert.equal(proj(readWork(editIndex(html, {proj: 'soualem', imgs: s.imgs, th: null})), 'soualem').th, undefined);
});

test('one category of a page with categories', () => {
  const p = proj(readWork(html), 'personal'), c2 = p.cats[1].imgs.slice(1);
  const after = proj(readWork(editIndex(html, {proj: 'personal', cat: 'C-02', imgs: c2})), 'personal');
  assert.deepEqual(after.cats[1].imgs, c2); assert.deepEqual(after.cats[0].imgs, p.cats[0].imgs);
});

test('labels.js round-trip, and the cache-buster follows its content', () => {
  assert.equal(writeLabels(labelsJs, readLabels(labelsJs)), labelsJs);
  const more = writeLabels(labelsJs, {...readLabels(labelsJs), 'zz-1': 'IMG_1 · 10:00:00 · 1/60 s · f/2 · ISO 100'});
  assert.notEqual(bumpLabels(html, more), bumpLabels(html, labelsJs));
  assert.match(bumpLabels(html, more), /labels\.js\?v=[0-9a-f]{8}"/);
});

test('archive records: removed, added, renumbered, featured; tags kept', () => {
  const photos = [{id: 'a', genres: ['concert'], alt: 'X, photo 1', featured: false, date: null}, {id: 'b', genres: [], alt: 'X, photo 2', featured: false}];
  const out = editPhotos(photos, {name: 'X', ids: ['n', 'b'], removed: ['a'], added: {n: {w: 600, h: 400, date: '2026-03-21'}}, featured: {b: true}});
  assert.deepEqual(out.map(r => r.id), ['b', 'n']);
  assert.equal(out.find(r => r.id === 'b').alt, 'X, photo 2'); assert.equal(out.find(r => r.id === 'b').featured, true);
  const n = out.find(r => r.id === 'n');
  assert.deepEqual([n.alt, n.year, n.date, n.thumb, n.w], ['X, photo 1', 2026, '2026-03-21', 'assets/archive/t/n.jpg', 600]);
});

test('new ids come from the file name and never clash', () => {
  const taken = new Set(['soualem-9173']);
  assert.equal(newId('soualem', 'IMG_9174.JPG', taken), 'soualem-9174');
  assert.equal(newId('soualem', 'IMG_9173.jpg', taken), 'soualem-9173-2');
});

// a JPEG holding only an EXIF block: 1/125 s, f/4.5, ISO 500, 2026:03:21 17:44:53
function jpegWithExif(){
  const b = new ArrayBuffer(200), v = new DataView(b), t = 12, le = true;
  v.setUint16(0, 0xFFD8); v.setUint16(2, 0xFFE1); v.setUint16(4, 190); v.setUint32(6, 0x45786966); v.setUint16(10, 0);
  v.setUint16(t, 0x4949); v.setUint16(t + 2, 42, le); v.setUint32(t + 4, 8, le);
  v.setUint16(t + 8, 1, le); v.setUint16(t + 10, 0x8769, le); v.setUint16(t + 12, 4, le); v.setUint32(t + 14, 1, le); v.setUint32(t + 18, 26, le);
  const e = (i, tag, type, cnt, val) => { const o = t + 26 + 2 + i * 12; v.setUint16(o, tag, le); v.setUint16(o + 2, type, le); v.setUint32(o + 4, cnt, le); v.setUint32(o + 8, val, le); };
  v.setUint16(t + 26, 4, le);
  e(0, 0x829A, 5, 1, 90); e(1, 0x829D, 5, 1, 98); e(2, 0x8827, 3, 1, 500); e(3, 0x9003, 2, 20, 106);
  v.setUint32(t + 90, 1, le); v.setUint32(t + 94, 125, le); v.setUint32(t + 98, 45, le); v.setUint32(t + 102, 10, le);
  [...'2026:03:21 17:44:53'].forEach((c, i) => v.setUint8(t + 106 + i, c.charCodeAt(0)));
  return b;
}

test('camera line from a JPG with camera data, none without', () => {
  assert.deepEqual(cameraLine(jpegWithExif(), 'IMG_9173-2.jpg'), {date: '2026-03-21', label: 'IMG_9173 · 17:44:53 · 1/125 s · f/4.5 · ISO 500'});
  assert.equal(cameraLine(readFileSync(join(ROOT, 'assets/home/soualem-9173.jpg')).buffer, 'x.jpg'), null);  // web copies carry no EXIF
});

test('Selected work per section: round-trip, then featured, else the defaults', () => {
  const w = readWork(html), photos = JSON.parse(readFileSync(join(ROOT, 'data/photos.json'), 'utf8')), none = photos.map(p => ({...p, featured: false}));
  const sel = {photography: ['soualem-9173', 'x19901_61074'], design: ['x190932_899304'], workshops: []};
  const set = editSelected(html, sel);
  assert.deepEqual(readSelected(set), sel);
  assert.deepEqual(readWork(set), w);  // the page list is untouched
  assert.deepEqual(selection(w, {photography: ['soualem-9173']}, photos.map(p => ({...p, featured: p.id === 'x19901_61074'}))), ['soualem-9173', 'x19901_61074']);
  assert.deepEqual(selection(w, {}, none), w[0].projects.filter(p => p.imgs).map(p => p.imgs.includes(p.th) ? p.th : p.imgs[0]));
  assert.deepEqual(selection(w, {photography: ['gone-id']}, []), w[0].projects.filter(p => p.imgs).map(p => p.imgs.includes(p.th) ? p.th : p.imgs[0]));  // unknown ids drop out
  assert.deepEqual(selection(w, sel, none, 'design'), ['x190932_899304']);
  const all = selection(w, {}, none, 'design'), firsts = w.find(s => s.id === 'design').projects.map(p => (p.imgs || p.cats[0].imgs)[0]);
  assert.deepEqual(all.slice(0, firsts.length), firsts);  // one per project first
  assert.equal(all.length, 39);
});

test('a new page goes after the last page of its group, else at the end of its section', () => {
  const ids = (h, sid) => readWork(h).find(s => s.id === sid).projects.map(p => p.id);
  const before = ids(html, 'photography');
  const places = insertProject(html, 'photography', {id: 'new-one', group: 'Places', name: "Jemaa's Night", info: '01.01.2026'});
  const after = ids(places, 'photography'), at = after.indexOf('new-one');
  assert.equal(after.length, before.length + 1);
  assert.equal(readWork(places)[0].projects[at - 1].group, 'Places'); assert.notEqual(readWork(places)[0].projects[at + 1]?.group, 'Places');
  assert.equal(readWork(places)[0].projects[at].name, "Jemaa's Night");  // quotes survive
  assert.deepEqual(readWork(places)[0].projects[at].imgs, []);
  const music = insertProject(html, 'photography', {id: 'm2', group: 'Music', name: 'M2'}), mi = ids(music, 'photography');
  const mp = readWork(music)[0].projects, k = mi.indexOf('m2');  // after the last Music page, not inside L'Boulevard's two lines
  assert.equal(mp[k - 1].group, 'Music'); assert.notEqual(mp[k + 1]?.group, 'Music'); assert.ok(mp.every(p => p.id !== 'boulevard' || p.doors));
  assert.equal(ids(insertProject(html, 'design', {id: 'p9', name: 'P9', poster: true}), 'design').at(-1), 'p9');
  assert.equal(readWork(insertProject(html, 'design', {id: 'p9', name: 'P9', poster: true}))[1].projects.at(-1).poster, true);
  assert.equal(ids(insertProject(html, 'photography', {id: 'g', group: 'Brand new', name: 'G'}), 'photography').at(-1), 'g');
});

test('page order: whole pages move, groups follow their first page, other sections untouched', () => {
  const ids = (h, sid) => readWork(h).find(s => s.id === sid).projects.map(p => p.id), ph = ids(html, 'photography');
  const want = [...ph.filter(id => readWork(html)[0].projects.find(p => p.id === id).group === 'Music').reverse(), ...ph.filter(id => readWork(html)[0].projects.find(p => p.id === id).group !== 'Music')];
  const out = orderProjects(html, 'photography', want), w = readWork(out);
  assert.deepEqual(ids(out, 'photography'), want);
  assert.ok(w[0].projects.find(p => p.id === 'boulevard').doors);  // a two-line page stays whole
  assert.equal(w[0].projects[0].group, 'Music');
  assert.deepEqual(readWork(out).slice(1), readWork(html).slice(1));
  const d = ids(html, 'design'), dout = orderProjects(html, 'design', [d.at(-1)]);  // ids left out keep their order after
  assert.deepEqual(ids(dout, 'design'), [d.at(-1), ...d.slice(0, -1)]);
  assert.deepEqual(readWork(dout)[1].projects.find(p => p.id === 'personal').cats, readWork(html)[1].projects.find(p => p.id === 'personal').cats);
  assert.equal(orderProjects(html, 'photography', ph), html);
});

test('rename: the page line only, quotes survive, categories keep theirs', () => {
  const w = readWork(editIndex(html, {proj: 'soualem', imgs: proj(readWork(html), 'soualem').imgs, name: "Soualem's Fields"}));
  assert.equal(proj(w, 'soualem').name, "Soualem's Fields"); assert.equal(proj(w, 'jazz').name, proj(readWork(html), 'jazz').name);
  const p = proj(readWork(html), 'personal'), c = readWork(editIndex(html, {proj: 'personal', cat: 'C-02', imgs: p.cats[1].imgs, name: 'Personal'}));
  assert.equal(proj(c, 'personal').name, 'Personal'); assert.deepEqual(proj(c, 'personal').cats.map(x => x.name), p.cats.map(x => x.name));
});
