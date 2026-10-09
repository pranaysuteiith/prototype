import { CONFIG } from '../config.js';
import { CATEGORIES, ITEMS } from '../core/catalog.js';
import { purchaseCheck, rewardFor } from '../core/economy.js';
import { MAX_NOTES, noteCheck, reduce } from '../core/game.js';
import { progressToNext, STAGES } from '../core/journey.js';
import { clearSave, loadGame, saveGame } from '../core/storage.js';
import * as Timer from '../core/timer.js';
import { renderRoom, roomKey } from './room.js';

// Browser shell: owns the single game state, feeds actions to the reducer,
// persists, and paints. All rules live in src/core.

const $ = (id) => document.getElementById(id);
const storage = safeLocalStorage();
const params = new URLSearchParams(location.search);
const debug = params.has('debug') ? params.get('debug') !== '0' : CONFIG.debug;

let state = loadGame(storage);
let lastLogId = state.nextId; // only toast entries created after load
let lastRoomKey = '';
let shopTab = 'furniture';

function dispatch(action) {
  const next = reduce(state, action, Date.now());
  if (next === state) return;
  const prev = state;
  state = next;
  saveGame(storage, state);
  render(prev);
}

// ------------------------------------------------------------------ render

function render(prev) {
  renderTimer();
  renderRoomIfChanged();
  renderHeader();
  renderJourney();
  renderShop();
  renderNotes();
  renderToasts();
  if (prev && prev.timer.status !== Timer.STATUS.COMPLETE && state.timer.status === Timer.STATUS.COMPLETE) {
    celebrate(prev);
  }
}

const PHASE_TEXT = {
  idle: 'Ready to start',
  running: 'Focusing',
  paused: 'Paused',
  complete: 'Complete',
};

const COMPANION_TEXT = {
  idle: 'Biscuit is napping. Start a session when you are ready.',
  running: 'Biscuit is keeping you company. Stay with it.',
  paused: 'Biscuit tilts their head. Back to it?',
  complete: 'Biscuit is thrilled! Coins are in your wallet.',
};

function renderTimer() {
  const now = Date.now();
  const { timer } = state;
  const phase = Timer.phaseOf(timer);
  const card = $('timer-card');
  card.dataset.phase = phase;
  card.dataset.status = timer.status;
  $('phase-badge').textContent = PHASE_TEXT[timer.status];
  $('clock').textContent = Timer.formatClock(Timer.remaining(timer, now));
  $('bar-fill').style.width = `${(Timer.progress(timer, now) * 100).toFixed(2)}%`;
  $('companion-line').textContent = COMPANION_TEXT[timer.status];

  const reward = rewardFor(timer);
  $('reward-hint').textContent =
    timer.status === Timer.STATUS.COMPLETE
      ? `+${reward.total} earned${timer.forced ? ' (dev)' : ''}`
      : `Earn ${CONFIG.coinsPerPomodoro}${timer.pauseCount === 0 ? ` +${CONFIG.unbrokenFocusBonus} unbroken` : ''}`;

  const clockHand = document.getElementById('clock-minute');
  if (clockHand) clockHand.setAttribute('transform', `rotate(${(Timer.progress(timer, now) * 360).toFixed(1)} 18 18)`);

  document.title = timer.status === Timer.STATUS.RUNNING ? `${$('clock').textContent} · Focus Rooms` : 'Focus Rooms';

  const controls = {
    idle: [['Start focus', 'timer/start', 'primary']],
    running: [['Pause', 'timer/pause', ''], ['Give up', 'timer/reset', 'ghost']],
    paused: [['Resume', 'timer/resume', 'primary'], ['Give up', 'timer/reset', 'ghost']],
    complete: [['Start next session', 'timer/reset', 'primary']],
  }[timer.status];
  const signature = timer.status;
  const box = $('controls');
  if (box.dataset.signature !== signature) {
    box.dataset.signature = signature;
    box.replaceChildren(
      ...controls.map(([label, type, variant]) => {
        const btn = document.createElement('button');
        btn.className = `btn ${variant}`;
        btn.textContent = label;
        btn.addEventListener('click', () => dispatch({ type }));
        return btn;
      }),
    );
  }

  const devComplete = $('dev-complete');
  devComplete.disabled = !(timer.status === Timer.STATUS.RUNNING || timer.status === Timer.STATUS.PAUSED);
  const durationSelect = $('dev-duration');
  durationSelect.disabled = timer.status !== Timer.STATUS.IDLE;
  if (document.activeElement !== durationSelect) durationSelect.value = String(timer.durationMs);
}

function renderRoomIfChanged() {
  const key = roomKey(state);
  if (key === lastRoomKey) return;
  lastRoomKey = key;
  $('room').innerHTML = renderRoom(state);
  renderTimer(); // re-apply the clock hand to the fresh SVG
}

function renderHeader() {
  $('coins').textContent = state.coins;
  $('sessions').textContent = state.sessionsCompleted;
  const stage = STAGES[state.stageReached];
  $('stage-index').textContent = `Stage ${state.stageReached + 1} of ${STAGES.length}`;
  $('stage-name').textContent = stage.name;
  $('stage-blurb').textContent = stage.blurb;
}

function renderJourney() {
  const prog = progressToNext(state.sessionsCompleted);
  $('journey-fill').style.width = `${((prog.done / prog.needed) * 100).toFixed(1)}%`;
  $('journey-next').textContent = prog.next === null ? 'Journey complete' : `${prog.needed - prog.done} to “${STAGES[prog.next].name}”`;
  $('journey').innerHTML = STAGES.map((stage, i) => {
    const cls = i < state.stageReached ? 'done' : i === state.stageReached ? 'current' : 'todo';
    const meta = i === 0 ? 'Start' : `${stage.sessions} session${stage.sessions === 1 ? '' : 's'} · +${stage.bonus}`;
    return `<li class="${cls}"><span class="dot"></span><span class="name">${stage.name}</span><span class="muted small">${meta}</span></li>`;
  }).join('');
}

function renderShop() {
  $('shop-tabs').innerHTML = CATEGORIES.map(
    (c) => `<button role="tab" class="tab ${c.id === shopTab ? 'active' : ''}" aria-selected="${c.id === shopTab}" data-tab="${c.id}">${c.label}</button>`,
  ).join('');
  const items = ITEMS.filter((item) => item.category === shopTab);
  $('shop').innerHTML = items
    .map((item) => {
      const check = purchaseCheck(state, item.id);
      const owned = Boolean(state.owned[item.id]);
      let action;
      if (owned) action = `<span class="tag owned">Owned</span>`;
      else if (check.reason === 'Locked') action = `<span class="tag locked">${STAGES[item.stage].name}</span>`;
      else action = `<button class="btn buy" data-buy="${item.id}" ${check.ok ? '' : 'disabled'} title="${check.reason || ''}"><span class="coin" aria-hidden="true"></span>${item.price}</button>`;
      const note = !owned && check.reason && check.reason !== 'Locked' ? `<span class="small warn">${check.reason}</span>` : '';
      return `<li class="shop-item ${owned ? 'is-owned' : ''} ${check.reason === 'Locked' ? 'is-locked' : ''}">
        <span class="swatch ${item.category}" aria-hidden="true"></span>
        <div class="shop-text"><b>${item.name}</b><span class="muted small">${item.description}</span>${note}</div>
        ${action}
      </li>`;
    })
    .join('');
}

function renderNotes() {
  const check = noteCheck(state, 'x');
  const hasBoard = Boolean(state.owned.corkboard);
  $('note-input').disabled = !hasBoard || state.notes.length >= MAX_NOTES;
  $('note-btn').disabled = !check.ok;
  $('note-btn').textContent = `Pin · ${CONFIG.noteCost}`;
  $('note-hint').textContent = hasBoard
    ? check.ok
      ? 'Notes appear on your corkboard. Hover them in the room to read.'
      : check.reason
    : 'Buy a Corkboard (Decor) to start writing on your walls.';
  $('notes-count').textContent = `${state.notes.length}/${MAX_NOTES}`;
  $('notes').innerHTML = state.notes
    .map((n) => `<li><span class="note-chip" style="background:${n.color}"></span><span class="note-text"></span><button class="icon-btn" data-remove="${n.id}" aria-label="Remove note">×</button></li>`)
    .join('');
  // Note text is user input: set it as text, never as HTML.
  [...$('notes').querySelectorAll('.note-text')].forEach((el, i) => (el.textContent = state.notes[i].text));
}

function renderToasts() {
  const fresh = state.log.filter((entry) => entry.id >= lastLogId);
  if (!fresh.length) return;
  lastLogId = state.log[state.log.length - 1].id + 1;
  for (const entry of fresh) {
    const el = document.createElement('div');
    el.className = `toast toast-${entry.kind}`;
    el.textContent = entry.text;
    $('toasts').append(el);
    while ($('toasts').childElementCount > 4) $('toasts').firstElementChild.remove();
    setTimeout(() => el.classList.add('out'), 2800);
    setTimeout(() => el.remove(), 3300);
  }
}

function celebrate(prev) {
  const earned = state.coins - prev.coins;
  const burst = $('burst');
  const el = document.createElement('div');
  el.className = 'coin-pop';
  el.innerHTML = `<span class="coin" aria-hidden="true"></span>+${earned}`;
  burst.replaceChildren(el);
  setTimeout(() => el.remove(), 2200);
}

// ------------------------------------------------------------------ input

$('shop-tabs').addEventListener('click', (e) => {
  const tab = e.target.closest('[data-tab]');
  if (!tab) return;
  shopTab = tab.dataset.tab;
  renderShop();
});

$('shop').addEventListener('click', (e) => {
  const btn = e.target.closest('[data-buy]');
  if (btn) dispatch({ type: 'shop/buy', itemId: btn.dataset.buy });
});

$('note-form').addEventListener('submit', (e) => {
  e.preventDefault();
  const input = $('note-input');
  const before = state.notes.length;
  dispatch({ type: 'notes/add', text: input.value });
  if (state.notes.length > before) input.value = '';
});

$('notes').addEventListener('click', (e) => {
  const btn = e.target.closest('[data-remove]');
  if (btn) dispatch({ type: 'notes/remove', id: Number(btn.dataset.remove) });
});

$('dev-complete').addEventListener('click', () => dispatch({ type: 'timer/completeNow' }));
$('dev-coins').addEventListener('click', () => dispatch({ type: 'debug/grantCoins', amount: 100 }));
$('dev-duration').addEventListener('change', (e) => dispatch({ type: 'timer/setDuration', ms: Number(e.target.value) }));
// Two-step confirm built into the button (browser dialogs are not always available).
let resetArmed = null;
$('dev-reset').addEventListener('click', (e) => {
  const btn = e.currentTarget;
  if (!resetArmed) {
    btn.textContent = 'Tap again to erase';
    resetArmed = setTimeout(() => {
      resetArmed = null;
      btn.textContent = 'Reset save';
    }, 3000);
    return;
  }
  clearTimeout(resetArmed);
  clearSave(storage);
  location.reload();
});

document.addEventListener('keydown', (e) => {
  if (e.target.closest('input, textarea, select') || e.metaKey || e.ctrlKey || e.altKey) return;
  if (e.code === 'Space') {
    e.preventDefault();
    const type = { idle: 'timer/start', running: 'timer/pause', paused: 'timer/resume', complete: 'timer/reset' }[state.timer.status];
    dispatch({ type });
  } else if (debug && e.key.toLowerCase() === 'c') {
    dispatch({ type: 'timer/completeNow' });
  }
});

// ------------------------------------------------------------------ boot

function safeLocalStorage() {
  try {
    return window.localStorage;
  } catch {
    return null;
  }
}

$('dev').hidden = !debug;
// Exposed for console testing: focusRooms.completeNow(), focusRooms.state
window.focusRooms = {
  get state() {
    return state;
  },
  dispatch,
  completeNow: () => dispatch({ type: 'timer/completeNow' }),
};

render(null);
// A session that ran out while the tab was closed settles on the first tick.
setInterval(() => {
  dispatch({ type: 'timer/tick' });
  if (state.timer.status === Timer.STATUS.RUNNING) renderTimer();
}, 250);
