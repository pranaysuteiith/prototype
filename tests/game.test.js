import assert from 'node:assert/strict';
import { test } from 'node:test';
import { CONFIG } from '../src/config.js';
import { ITEMS } from '../src/core/catalog.js';
import { purchaseCheck } from '../src/core/economy.js';
import { createGame, growthOf, reduce, STARTING_COINS } from '../src/core/game.js';
import { progressToNext, stageFor, STAGES } from '../src/core/journey.js';

const HOUR = 60 * 60_000;
const play = (state, ...actions) => actions.reduce((s, [a, now = 0]) => reduce(s, a, now), state);
const session = (state, { pause = false } = {}) =>
  play(
    state,
    [{ type: 'timer/start' }, 0],
    ...(pause ? [[{ type: 'timer/pause' }, 10], [{ type: 'timer/resume' }, 20]] : []),
    [{ type: 'timer/tick' }, HOUR + 20],
    [{ type: 'timer/reset' }],
  );
const rich = (coins = 10_000) => reduce(createGame(), { type: 'debug/grantCoins', amount: coins }, 0);

test('a completed unbroken session pays base + bonus', () => {
  const s = play(createGame(), [{ type: 'timer/start' }, 0], [{ type: 'timer/tick' }, HOUR]);
  assert.equal(s.timer.status, 'complete');
  assert.equal(s.coins, STARTING_COINS + CONFIG.coinsPerPomodoro + CONFIG.unbrokenFocusBonus + STAGES[1].bonus);
  assert.equal(s.sessionsCompleted, 1);
});

test('pausing forfeits the unbroken bonus but still pays the base', () => {
  const s = session(createGame(), { pause: true });
  assert.equal(s.coins, STARTING_COINS + CONFIG.coinsPerPomodoro + STAGES[1].bonus);
});

test('on-demand completion pays out like a real session', () => {
  const s = play(createGame(), [{ type: 'timer/start' }, 0], [{ type: 'timer/completeNow' }, 5]);
  assert.equal(s.timer.status, 'complete');
  assert.equal(s.timer.forced, true);
  assert.equal(s.sessionsCompleted, 1);
});

test('coins are awarded once per session, however many ticks follow', () => {
  let s = play(createGame(), [{ type: 'timer/start' }, 0], [{ type: 'timer/completeNow' }, 5]);
  const coins = s.coins;
  for (let i = 0; i < 5; i++) s = reduce(s, { type: 'timer/tick' }, HOUR * (i + 2));
  s = reduce(s, { type: 'timer/completeNow' }, HOUR * 9);
  assert.equal(s.coins, coins);
  assert.equal(s.sessionsCompleted, 1);
});

test('giving up mid-session pays nothing', () => {
  const s = play(createGame(), [{ type: 'timer/start' }, 0], [{ type: 'timer/reset' }, 30 * 60_000]);
  assert.equal(s.coins, STARTING_COINS);
  assert.equal(s.sessionsCompleted, 0);
  assert.equal(s.timer.status, 'idle');
  assert.match(s.log.at(-1).text, /abandoned/);
});

test('starting coins buy the first desk and chair', () => {
  const s = play(createGame(), [{ type: 'shop/buy', itemId: 'desk' }], [{ type: 'shop/buy', itemId: 'chair' }]);
  assert.ok(s.owned.desk && s.owned.chair);
  assert.equal(s.coins, STARTING_COINS - 35);
});

test('purchases respect price, stage locks and requirements', () => {
  const poor = createGame();
  assert.equal(purchaseCheck({ ...poor, coins: 0 }, 'desk').reason, 'Not enough coins');
  assert.equal(purchaseCheck(rich(), 'computer').reason, 'Locked');
  assert.match(purchaseCheck({ ...rich(), stageReached: 1 }, 'computer').reason, /Needs Oak Desk/);

  const blocked = reduce({ ...rich(), stageReached: 1 }, { type: 'shop/buy', itemId: 'computer' }, 0);
  assert.equal(blocked.owned.computer, undefined);
  assert.equal(blocked.log.at(-1).kind, 'error');

  const owned = play(rich(), [{ type: 'shop/buy', itemId: 'desk' }]);
  assert.equal(purchaseCheck(owned, 'desk').reason, 'Owned');
  assert.equal(reduce(owned, { type: 'shop/buy', itemId: 'nope' }, 0).log.at(-1).text, 'Unknown item');
});

test('every catalog item can eventually be bought', () => {
  let s = { ...rich(100_000), stageReached: STAGES.length - 1 };
  // Buy in catalog order, retrying until requirements resolve.
  for (let pass = 0; pass < 3; pass++) for (const item of ITEMS) s = reduce(s, { type: 'shop/buy', itemId: item.id }, 0);
  assert.deepEqual(Object.keys(s.owned).sort(), ITEMS.map((i) => i.id).sort());
});

test('journey stages unlock by completed sessions and pay their bonus once', () => {
  assert.equal(stageFor(0), 0);
  assert.equal(stageFor(1), 1);
  assert.equal(stageFor(2), 1);
  assert.equal(stageFor(15), STAGES.length - 1);
  assert.equal(stageFor(500), STAGES.length - 1);
  assert.deepEqual(progressToNext(4), { current: 2, next: 3, done: 1, needed: 3 });

  let s = createGame();
  let bonuses = 0;
  for (let i = 1; i <= 15; i++) {
    const before = s.stageReached;
    s = session(s);
    if (s.stageReached > before) bonuses += STAGES[s.stageReached].bonus;
  }
  assert.equal(s.stageReached, STAGES.length - 1);
  const perSession = CONFIG.coinsPerPomodoro + CONFIG.unbrokenFocusBonus;
  assert.equal(s.coins, STARTING_COINS + 15 * perSession + bonuses);
  assert.equal(bonuses, STAGES.reduce((sum, st) => sum + st.bonus, 0));
});

test('notes need a corkboard, cost coins, and are validated', () => {
  let s = rich(100);
  s = reduce(s, { type: 'notes/add', text: 'Ship it' }, 0);
  assert.equal(s.notes.length, 0, 'no corkboard yet');

  s = reduce({ ...s, stageReached: 1 }, { type: 'shop/buy', itemId: 'corkboard' }, 0);
  const coins = s.coins;
  s = reduce(s, { type: 'notes/add', text: '  Ship it  ' }, 0);
  assert.equal(s.notes.length, 1);
  assert.equal(s.notes[0].text, 'Ship it');
  assert.equal(s.coins, coins - CONFIG.noteCost);

  assert.equal(reduce(s, { type: 'notes/add', text: '   ' }, 0).notes.length, 1);
  assert.equal(reduce(s, { type: 'notes/add', text: 'x'.repeat(CONFIG.noteMaxLength + 1) }, 0).notes.length, 1);

  for (let i = 0; i < 10; i++) s = reduce(s, { type: 'notes/add', text: `note ${i}` }, 0);
  assert.equal(s.notes.length, 6, 'corkboard holds six');

  s = reduce(s, { type: 'notes/remove', id: s.notes[0].id }, 0);
  assert.equal(s.notes.length, 5);
});

test('duration can only change while idle', () => {
  const s = reduce(createGame(), { type: 'timer/setDuration', ms: 10_000 }, 0);
  assert.equal(s.timer.durationMs, 10_000);
  const running = reduce(s, { type: 'timer/start' }, 0);
  assert.equal(reduce(running, { type: 'timer/setDuration', ms: HOUR }, 0), running);
});

test('plants grow one step every two sessions after purchase, capped at 2', () => {
  let s = reduce({ ...rich(), stageReached: 1 }, { type: 'shop/buy', itemId: 'plant' }, 0);
  assert.equal(growthOf(s, 'plant'), 0);
  s = session(session(s));
  assert.equal(growthOf(s, 'plant'), 1);
  for (let i = 0; i < 6; i++) s = session(s);
  assert.equal(growthOf(s, 'plant'), 2);
  assert.equal(growthOf(s, 'cat'), 0);
});
