import { CONFIG } from '../config.js';
import { getItem } from './catalog.js';
import { purchaseCheck, rewardFor } from './economy.js';
import { STAGES, stageFor } from './journey.js';
import * as Timer from './timer.js';

// Whole-game state and the single reducer that changes it. The UI only ever
// calls reduce(); this keeps every rule testable without a browser.

export const STARTING_COINS = 40;
export const MAX_NOTES = 6;
const NOTE_COLORS = ['#f6d66b', '#f4a988', '#a8d5a2', '#9cc7e8', '#e3b5e0', '#f7f1e3'];
const LOG_LIMIT = 30;

export function createGame(config = CONFIG) {
  return {
    version: 1,
    coins: STARTING_COINS,
    lifetimeCoins: 0,
    sessionsCompleted: 0,
    stageReached: 0,
    owned: {}, // itemId -> { boughtAtSession }
    notes: [], // { id, text, color }
    timer: Timer.createTimer(config.pomodoroMinutes * 60_000),
    log: [], // { id, kind, text } newest last; the UI turns these into toasts
    nextId: 1,
  };
}

export function reduce(state, action, now, config = CONFIG) {
  switch (action.type) {
    case 'timer/start':
      return withTimer(state, Timer.start(state.timer, now), now, config);
    case 'timer/pause':
      return withTimer(state, Timer.pause(state.timer, now), now, config);
    case 'timer/resume':
      return withTimer(state, Timer.resume(state.timer, now), now, config);
    case 'timer/tick':
      return withTimer(state, Timer.tick(state.timer, now), now, config);
    case 'timer/completeNow':
      return withTimer(state, Timer.completeNow(state.timer, now), now, config);
    case 'timer/reset':
      return resetTimer(state);
    case 'timer/setDuration':
      return setDuration(state, action.ms);
    case 'shop/buy':
      return buy(state, action.itemId);
    case 'notes/add':
      return addNote(state, action.text, config);
    case 'notes/remove':
      return { ...state, notes: state.notes.filter((n) => n.id !== action.id) };
    case 'debug/grantCoins':
      return log({ ...state, coins: state.coins + action.amount }, 'debug', `+${action.amount} coins (dev)`);
    default:
      return state;
  }
}

// Applies a timer transition and pays out exactly once when it completes.
function withTimer(state, timer, now, config) {
  if (timer === state.timer) return state;
  let next = { ...state, timer };
  const justCompleted = state.timer.status !== Timer.STATUS.COMPLETE && timer.status === Timer.STATUS.COMPLETE;
  if (justCompleted) next = settleSession(next, config);
  return next;
}

function settleSession(state, config) {
  const reward = rewardFor(state.timer, config);
  const sessionsCompleted = state.sessionsCompleted + 1;
  let next = {
    ...state,
    coins: state.coins + reward.total,
    lifetimeCoins: state.lifetimeCoins + reward.total,
    sessionsCompleted,
  };
  const bonusText = reward.bonus ? ` (incl. +${reward.bonus} unbroken focus)` : '';
  next = log(next, 'reward', `Session complete! +${reward.total} coins${bonusText}`);

  const target = stageFor(sessionsCompleted);
  while (next.stageReached < target) {
    const stageReached = next.stageReached + 1;
    const stage = STAGES[stageReached];
    next = { ...next, stageReached, coins: next.coins + stage.bonus, lifetimeCoins: next.lifetimeCoins + stage.bonus };
    next = log(next, 'stage', `Journey: “${stage.name}” reached. +${stage.bonus} coins`);
  }
  return next;
}

function resetTimer(state) {
  const { status } = state.timer;
  const abandoned = status === Timer.STATUS.RUNNING || status === Timer.STATUS.PAUSED;
  const next = { ...state, timer: Timer.reset(state.timer) };
  return abandoned ? log(next, 'info', 'Session abandoned. No coins this time.') : next;
}

function setDuration(state, ms) {
  if (state.timer.status !== Timer.STATUS.IDLE || !(ms > 0)) return state;
  return { ...state, timer: Timer.createTimer(ms) };
}

function buy(state, itemId) {
  const check = purchaseCheck(state, itemId);
  if (!check.ok) return log(state, 'error', check.reason);
  const item = getItem(itemId);
  const next = {
    ...state,
    coins: state.coins - item.price,
    owned: { ...state.owned, [itemId]: { boughtAtSession: state.sessionsCompleted } },
  };
  return log(next, 'purchase', `${item.name} added to your room`);
}

export function noteCheck(state, text, config = CONFIG) {
  if (!state.owned.corkboard) return { ok: false, reason: 'Buy a Corkboard to pin notes' };
  if (state.notes.length >= MAX_NOTES) return { ok: false, reason: 'Corkboard is full' };
  const trimmed = (text || '').trim();
  if (!trimmed) return { ok: false, reason: 'Write something first' };
  if (trimmed.length > config.noteMaxLength) return { ok: false, reason: `Keep it under ${config.noteMaxLength} characters` };
  if (state.coins < config.noteCost) return { ok: false, reason: 'Not enough coins' };
  return { ok: true, reason: null };
}

function addNote(state, text, config) {
  const check = noteCheck(state, text, config);
  if (!check.ok) return log(state, 'error', check.reason);
  const note = { id: state.nextId, text: text.trim(), color: NOTE_COLORS[state.nextId % NOTE_COLORS.length] };
  const next = { ...state, coins: state.coins - config.noteCost, notes: [...state.notes, note], nextId: state.nextId + 1 };
  return log(next, 'note', 'Note pinned to the corkboard');
}

function log(state, kind, text) {
  const entry = { id: state.nextId, kind, text };
  return { ...state, nextId: state.nextId + 1, log: [...state.log, entry].slice(-LOG_LIMIT) };
}

// Growth stage (0–2) for living things: one step every two sessions owned.
export function growthOf(state, itemId) {
  const owned = state.owned[itemId];
  if (!owned) return 0;
  return Math.min(2, Math.floor((state.sessionsCompleted - owned.boughtAtSession) / 2));
}
