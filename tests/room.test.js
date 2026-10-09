import assert from 'node:assert/strict';
import { test } from 'node:test';
import { ITEMS } from '../src/core/catalog.js';
import { createGame, reduce } from '../src/core/game.js';
import { renderRoom, roomKey } from '../src/ui/room.js';

const everything = () => {
  let s = { ...reduce(createGame(), { type: 'debug/grantCoins', amount: 100_000 }, 0), stageReached: 5 };
  for (let pass = 0; pass < 3; pass++) for (const item of ITEMS) s = reduce(s, { type: 'shop/buy', itemId: item.id }, 0);
  return s;
};

test('renders an empty room and a fully furnished one without NaN', () => {
  for (const s of [createGame(), everything()]) {
    const svg = renderRoom(s);
    assert.match(svg, /^<svg/);
    assert.doesNotMatch(svg, /NaN|undefined/);
  }
});

test('the dog reflects every timer state', () => {
  let s = createGame();
  assert.match(renderRoom(s), /class="zzz"/, 'asleep while idle');
  s = reduce(s, { type: 'timer/start' }, 0);
  assert.match(renderRoom(s), /class="wag"/, 'awake while running');
  s = reduce(s, { type: 'timer/pause' }, 1);
  assert.match(renderRoom(s), /class="tilt"/, 'curious while paused');
  s = reduce(s, { type: 'timer/completeNow' }, 2);
  assert.match(renderRoom(s), /class="bounce"/, 'celebrating when complete');
});

test('note text is escaped inside the SVG', () => {
  let s = everything();
  s = reduce(s, { type: 'notes/add', text: '<script>alert(1)</script>' }, 0);
  const svg = renderRoom(s);
  assert.doesNotMatch(svg, /<script>/);
  assert.match(svg, /&lt;script&gt;/);
});

test('room key changes on purchases and timer status but not on ticks', () => {
  const a = createGame();
  const b = reduce(a, { type: 'shop/buy', itemId: 'desk' }, 0);
  assert.notEqual(roomKey(a), roomKey(b));
  const running = reduce(b, { type: 'timer/start' }, 0);
  assert.notEqual(roomKey(b), roomKey(running));
  assert.equal(roomKey(running), roomKey(reduce(running, { type: 'timer/tick' }, 1000)));
});
