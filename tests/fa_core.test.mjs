// Unit tests for the archive's pure filter logic (pf-coe.1, pf-coe.2). Run: node --test tests/
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { emptyState, applyFilters, computeOptions, changeGenre, sortPhotos, slugify } from '../assets/archive/core.js';

const fx = f => JSON.parse(readFileSync(new URL(`fixtures/fa/${f}.json`, import.meta.url)));
const D = { taxonomy: fx('taxonomy'), refs: fx('refs'), photos: fx('photos'), series: fx('series') }, P = D.photos;
const ids = r => r.map(p => p.id);

test('parent genre matches any leaf', () => assert.equal(applyFilters(P, {...emptyState(), genre:'music'}, D).length, 8));
test('AC1 concert from all places', () => assert.deepEqual(ids(applyFilters(P, {...emptyState(), genre:'concert'}, D)).sort(), ['test-01','test-02','test-03','test-04','test-12']));
test('AC2 + place narrows, AND across', () => assert.equal(applyFilters(P, {...emptyState(), genre:'concert', location:['american-arts-center']}, D).length, 4));
test('AC3 + year narrows', () => assert.deepEqual(ids(applyFilters(P, {...emptyState(), genre:'concert', location:['american-arts-center'], year:['2026']}, D)), ['test-02','test-03']));
test('OR inside a filter', () => assert.equal(applyFilters(P, {...emptyState(), location:['seamens-club','test-venue-rabat']}, D).length, 2));
test('city derived from place, or from the photo', () => assert.equal(applyFilters(P, {...emptyState(), city:['casablanca']}, D).length, 10));
test('missing metadata never matches and never throws', () => { const r = ids(applyFilters(P, {...emptyState(), year:['2025']}, D)); assert.ok(!r.includes('test-09')); });
test('AC5 empty state = whole archive', () => assert.equal(applyFilters(P, emptyState(), D).length, 12));
test('untagged photo only under All', () => assert.ok(!ids(applyFilters(P, {...emptyState(), genre:'street'}, D)).includes('test-11')));
test('sort: date desc, undated last, id tiebreak', () => assert.deepEqual(ids(sortPhotos(P)), ['test-06','test-07','test-04','test-02','test-03','test-11','test-05','test-10','test-12','test-01','test-08','test-09']));
test('options: counts from the other filters', () => { const o = computeOptions(P, {...emptyState(), genre:'concert'}, D);
  assert.deepEqual(o.groups.location.map(x => [x.id, x.count]), [['american-arts-center',4],['seamens-club',1]]);
  assert.deepEqual(o.groups.year.map(x => [x.id, x.count]), [['2025',2],['2026',3]]);
  assert.equal(o.groups.city, undefined);   // one choice and nothing selected → hidden
  assert.equal(o.groups.client, undefined); });
test('options: genres with counts, empty parent hidden', () => { const g = computeOptions(P, emptyState(), D).genres;
  assert.deepEqual(g.map(x => [x.id, x.count]), [['music',8],['street',5]]);
  assert.deepEqual(g[0].children.map(x => [x.id, x.count]), [['concert',5],['festival',3]]); });
test('options: a selected value stays listed', () => assert.ok(computeOptions(P, {...emptyState(), client:['test-client']}, D).groups.client));
test('AC4 genre change drops only zero-match values', () => assert.deepEqual(
  changeGenre({...emptyState(), genre:'concert', location:['american-arts-center'], year:['2026']}, 'festival', P, D),
  {...emptyState(), genre:'festival', year:['2026']}));
test('AC4 genre change keeps values that still match', () => assert.deepEqual(
  changeGenre({...emptyState(), genre:'concert', location:['american-arts-center'], year:['2025']}, 'portraits', P, D),
  {...emptyState(), genre:'portraits', location:['american-arts-center'], year:['2025']}));
test('genre change never leaves an empty result', () => { const s = changeGenre({...emptyState(), genre:'concert', year:['2025'], artist:['test-band-b']}, 'festival', P, D);
  assert.ok(applyFilters(P, s, D).length > 0); });
test('slugify', () => { assert.equal(slugify("L'Boulevard 2025"), 'l-boulevard-2025'); assert.equal(slugify('Jinān Al Andalus'), 'jinan-al-andalus'); });
