// Checks the real archive data in data/ (pf-coe.3). Run: node --test 'tests/*.test.mjs'
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync, mkdtempSync, cpSync, writeFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { validate, computeOptions, emptyState, photosJson } from '../assets/archive/core.js';

const ROOT = fileURLToPath(new URL('..', import.meta.url));
const load = dir => Object.fromEntries(['taxonomy', 'refs', 'photos', 'series'].map(f => [f, JSON.parse(readFileSync(join(dir, `${f}.json`)))]));
const D = load(join(ROOT, 'data'));

test('every photo valid', () => { assert.ok(D.photos.length > 0); assert.deepEqual(validate(D), []); });
test('every image and thumb exists, with size', () => { for (const p of D.photos) {
  assert.ok(existsSync(join(ROOT, p.image)), p.image); assert.ok(existsSync(join(ROOT, p.thumb)), p.thumb); assert.ok(p.w > 0 && p.h > 0, p.id); } });
test('no invented genres yet', () => assert.ok(D.photos.every(p => p.genres.length === 0)));
test('misfiled Noches photo left out', () => assert.ok(!D.photos.some(p => p.id === 'x558783_464613')));
test('facts copied, not invented', () => { const by = Object.fromEntries(D.photos.map(p => [p.id, p]));
  assert.deepEqual([by.x839456_462094.locationId, by.x839456_462094.date, by.x839456_462094.artistIds], ['american-arts-center', '2025-06-13', ['ayoub-hattab']]);
  assert.equal(by.x714252_433206.date, null);
  assert.deepEqual(by['lbv-band-frame-02'].artistIds, ['suicide-machine']);
  assert.equal(by['lbv-band-frame-02'].locationId, null); });
test('room series keep room order', () => assert.equal(D.series.find(s => s.id === 'connection').photoIds[0], 'lbv-band-frame-03'));
test('with nothing tagged the genre row is hidden', () => assert.deepEqual(computeOptions(D.photos, emptyState(), D).genres, []));
test('re-running migration keeps edited records', () => {
  const tmp = mkdtempSync(join(tmpdir(), 'fa-')); cpSync(join(ROOT, 'data'), tmp, {recursive: true});
  const photos = JSON.parse(readFileSync(join(tmp, 'photos.json')));
  photos[0].genres = ['concert']; photos[0].alt = 'edited by hand';
  writeFileSync(join(tmp, 'photos.json'), photosJson(photos));
  execFileSync('node', ['scripts/fa_migrate.mjs'], {cwd: ROOT, env: {...process.env, FA_DATA: tmp}, stdio: 'pipe'});
  const after = JSON.parse(readFileSync(join(tmp, 'photos.json')));
  assert.equal(after.length, photos.length); assert.deepEqual(after[0], photos[0]);
});
