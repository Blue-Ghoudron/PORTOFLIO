// Page editor: the text edits behind tools/pages.html, kept pure so node can test them (tests/pages.test.mjs).
// Same formats as scripts/add_page.py: one WORK line per project, labels.js sorted, photos.json one record per line.
import { photosJson } from '../assets/archive/core.js';
export { photosJson };

export const readWork = html => {
  const start = html.indexOf('const WORK = ') + 13;
  return new Function('return ' + html.slice(start, html.indexOf('];\n', start) + 1))();
};

export const readLabels = js => Object.fromEntries([...js.matchAll(/^"([^"]+)": "([^"]*)"/gm)].map(m => [m[1], m[2]]));
export const writeLabels = (js, labels) => js.slice(0, js.indexOf('const LABELS = {')) + 'const LABELS = {\n'
  + Object.keys(labels).sort().map(k => `"${k}": "${labels[k]}"`).join(',\n') + '\n};\n';

// short content hash for the labels.js?v= cache-buster (FNV-1a)
export const version = text => { let h = 0x811c9dc5; for (const c of text) h = Math.imul(h ^ c.codePointAt(0), 0x1000193) >>> 0; return h.toString(16).padStart(8, '0'); };

const list = ids => '[' + ids.map(i => JSON.stringify(i)).join(', ') + ']';
const q = s => "'" + s.replace(/\\/g, '\\\\').replace(/'/g, "\\'") + "'";

/** One page's photos (or one category's) and its menu photo, written back into index.html. th: an id sets it, null drops it (the menu then shows the first photo). */
export function editIndex(html, {proj, cat, imgs, th}){
  const lines = html.split('\n'), at = lines.findIndex(l => l.startsWith(`    {id:'${proj}',`));
  if (at < 0) throw new Error(`no WORK line for ${proj}`);
  const target = cat ? lines.findIndex((l, i) => i > at && l.includes(`{name:${q(cat)},`)) : at;
  if (target < 0) throw new Error(`no category ${cat} in ${proj}`);
  lines[target] = lines[target].replace(/imgs:\[[^\]]*\]/, 'imgs:' + list(imgs));
  if (th === null) lines[at] = lines[at].replace(/\bth:'[^']*', /, '');
  else if (th) lines[at] = /\bth:'[^']*'/.test(lines[at]) ? lines[at].replace(/\bth:'[^']*'/, `th:${q(th)}`) : lines[at].replace(', info:', `, th:${q(th)}, info:`);
  return lines.join('\n');
}

export const bumpLabels = (html, labelsJs) => html.replace(/assets\/home\/labels\.js(\?v=\w+)?"/, `assets/home/labels.js?v=${version(labelsJs)}"`);

/** Archive records of a photo page: drop removed, add new ones, renumber alt, set featured; tags stay as they are. */
export function editPhotos(photos, {name, ids, removed = [], added = {}, featured = {}}){
  const gone = new Set(removed), out = photos.filter(r => !gone.has(r.id)), by = new Map(out.map(r => [r.id, r]));
  ids.forEach((id, n) => {
    let r = by.get(id);
    if (!r && added[id]) {
      const a = added[id];
      r = {id, title: null, image: `assets/home/${id}.jpg`, thumb: `assets/archive/t/${id}.jpg`, w: a.w, h: a.h, discipline: 'photography', genres: [],
        locationId: null, cityId: null, year: a.date ? +a.date.slice(0, 4) : null, date: a.date || null, eventIds: [], artistIds: [], clientId: null, featured: false, alt: ''};
      out.push(r); by.set(id, r);
    }
    if (!r) return;
    r.alt = `${name}, photo ${n + 1}`;
    if (id in featured) r.featured = featured[id];
  });
  return out;
}

const slug = s => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
/** <page>-<number from the file name>, unique among taken ids. */
export function newId(page, fileName, taken){
  const base = `${page}-${slug(fileName.replace(/\.[^.]+$/, '').replace(/^[A-Za-z]+_/, '')) || 'photo'}`;
  let id = base; for (let n = 2; taken.has(id); n++) id = `${base}-${n}`;
  return id;
}

/** Camera line from a JPG's own EXIF ("IMG_9173 · 17:44:53 · 1/100 s · f/5 · ISO 100") and its date, or null. */
export function cameraLine(buf, fileName){
  const v = new DataView(buf);
  if (v.byteLength < 4 || v.getUint16(0) !== 0xFFD8) return null;
  for (let o = 2; o + 10 < v.byteLength;) {
    const m = v.getUint16(o), len = v.getUint16(o + 2);
    if (m === 0xFFE1 && v.getUint32(o + 4) === 0x45786966) return fromTiff(v, o + 10, fileName);
    if ((m & 0xFF00) !== 0xFF00 || m === 0xFFDA) return null;
    o += 2 + len;
  }
  return null;
}
function fromTiff(v, t, fileName){
  const le = v.getUint16(t) === 0x4949, u16 = o => v.getUint16(o, le), u32 = o => v.getUint32(o, le);
  const ifd = off => {
    const tags = {}, n = u16(t + off);
    for (let i = 0; i < n; i++) {
      const e = t + off + 2 + i * 12, tag = u16(e), type = u16(e + 2), cnt = u32(e + 4);
      const at = (type === 2 && cnt > 4) || type === 5 ? t + u32(e + 8) : e + 8;
      tags[tag] = type === 2 ? String.fromCharCode(...new Uint8Array(v.buffer, v.byteOffset + at, cnt)).replace(/\0.*$/, '')
        : type === 3 ? u16(at) : type === 4 ? u32(at) : type === 5 ? u32(at) / u32(at + 4) : null;
    }
    return tags;
  };
  const ex = ifd(u32(t + 4))[0x8769];
  if (!ex) return null;
  const e = ifd(ex), when = e[0x9003], sh = e[0x829A], f = e[0x829D], iso = e[0x8827];
  if (!when || !sh || !f || !iso) return null;
  const name = (fileName.match(/^[A-Za-z]+_?\d+/) || [fileName.replace(/\.[^.]+$/, '')])[0];
  return {date: when.slice(0, 10).replace(/:/g, '-'),
    label: `${name} · ${when.slice(11)} · ${sh < 1 ? `1/${Math.round(1 / sh)} s` : `${+sh.toPrecision(6)} s`} · f/${+f.toFixed(2)} · ISO ${iso}`};
}
