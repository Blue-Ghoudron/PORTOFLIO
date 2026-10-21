// Unit tests for the archive's pure filter logic (pf-coe.1, pf-coe.2). Run: node --test 'tests/*.test.mjs'
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { emptyState, applyFilters, computeOptions, changeGenre, sortPhotos, slugify, parseQuery, serializeQuery, validate, photosJson } from '../assets/archive/core.js';

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

test('AC7 round trip', () => { const s = {...emptyState(), genre:'concert', location:['american-arts-center','seamens-club'], year:['2026']};
  const q = serializeQuery(s); assert.equal(q, 'genre=concert&location=american-arts-center,seamens-club&year=2026');
  assert.deepEqual(parseQuery(q, D), s); });
test('empty state serialises to nothing', () => assert.equal(serializeQuery(emptyState()), ''));
test('AC7 invalid params ignored', () => assert.deepEqual(
  parseQuery('genre=nope&year=abc,2025&location=american-arts-center,ghost&foo=1', D),
  {...emptyState(), year:['2025'], location:['american-arts-center']}));
test('garbage query does not throw', () => assert.deepEqual(parseQuery('%%%&&==', D), emptyState()));
test('fixtures are valid', () => assert.deepEqual(validate(D), []));
test('validation catches broken references', () => { const bad = structuredClone(D);
  bad.photos[0].genres = ['jazz']; bad.photos[1].locationId = 'ghost'; bad.photos.push({...bad.photos[2]}); bad.series[0].photoIds.push('test-99');
  const e = validate(bad).join('\n');
  for (const s of ['unknown genre "jazz"', 'unknown location "ghost"', 'duplicate id test-03', 'series test-series: unknown photo test-99']) assert.ok(e.includes(s), s); });
test('photosJson writes one record per line', () => assert.equal(photosJson(P.slice(0, 2)).split('\n').length, 5));
test('photosJson matches the fixture file byte for byte', () => assert.equal(photosJson(P), readFileSync(new URL('fixtures/fa/photos.json', import.meta.url), 'utf8')));
test('genre options ignore place/year so any genre can be picked (AC4)', () => {
  const g = computeOptions(P, {...emptyState(), genre:'concert', location:['seamens-club']}, D).genres;
  assert.deepEqual(g[0].children.map(x => [x.id, x.count]), [['concert',5],['festival',3]]); });
