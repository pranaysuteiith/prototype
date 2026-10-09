import assert from 'node:assert/strict';
import { test } from 'node:test';
import { CONFIG } from '../src/config.js';
import { createGame, reduce } from '../src/core/game.js';
import { loadGame, saveGame } from '../src/core/storage.js';

const memoryStorage = () => {
  const map = new Map();
  return { getItem: (k) => map.get(k) ?? null, setItem: (k, v) => map.set(k, v), removeItem: (k) => map.delete(k) };
};
const throwingStorage = { getItem() { throw new Error('blocked'); }, setItem() { throw new Error('blocked'); } };

test('round-trips a game through storage', () => {
  const store = memoryStorage();
  let s = reduce(createGame(), { type: 'shop/buy', itemId: 'desk' }, 0);
  s = reduce(s, { type: 'timer/start' }, 1234);
  assert.equal(saveGame(store, s), true);
  const loaded = loadGame(store);
  assert.ok(loaded.owned.desk);
  assert.equal(loaded.coins, s.coins);
  assert.equal(loaded.timer.status, 'running');
  assert.equal(loaded.timer.startedAt, 1234, 'a running session survives a reload');
  assert.deepEqual(loaded.log, [], 'toasts are not replayed');
});

test('missing, corrupt or blocked storage falls back to a new game', () => {
  assert.deepEqual(loadGame(null), createGame());
  assert.deepEqual(loadGame(throwingStorage), createGame());
  assert.equal(saveGame(throwingStorage, createGame()), false);
  const store = memoryStorage();
  store.setItem(CONFIG.saveKey, '{not json');
  assert.deepEqual(loadGame(store), createGame());
  store.setItem(CONFIG.saveKey, JSON.stringify({ version: 999 }));
  assert.deepEqual(loadGame(store), createGame());
});
