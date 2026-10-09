// Pomodoro timer as a pure state machine.
//
//   idle ──start──▶ running ──pause──▶ paused
//                     │  ▲               │
//                     │  └────resume─────┘
//                     │
//        (time runs out | completeNow)        reset (from any state)
//                     ▼                            ▼
//                  complete ─────────reset──────▶ idle
//
// Every function takes the current timer state plus `now` (ms timestamp) and
// returns a new state; nothing reads the clock itself, so tests can drive
// time directly. Invalid transitions return the state unchanged.

export const STATUS = Object.freeze({
  IDLE: 'idle',
  RUNNING: 'running',
  PAUSED: 'paused',
  COMPLETE: 'complete',
});

// The three player-facing phases the UI distinguishes.
export const PHASE = Object.freeze({
  START: 'start',
  ONGOING: 'ongoing',
  COMPLETE: 'complete',
});

export function createTimer(durationMs) {
  return {
    status: STATUS.IDLE,
    durationMs,
    startedAt: null, // wall-clock time of the current running stretch
    elapsedMs: 0, // time banked before the current running stretch
    pauseCount: 0,
    completedAt: null,
    forced: false, // true when finished via completeNow
  };
}

export function phaseOf(timer) {
  if (timer.status === STATUS.IDLE) return PHASE.START;
  if (timer.status === STATUS.COMPLETE) return PHASE.COMPLETE;
  return PHASE.ONGOING;
}

export function elapsed(timer, now) {
  if (timer.status === STATUS.RUNNING) {
    return Math.min(timer.durationMs, timer.elapsedMs + (now - timer.startedAt));
  }
  if (timer.status === STATUS.COMPLETE) return timer.durationMs;
  return timer.elapsedMs;
}

export function remaining(timer, now) {
  return Math.max(0, timer.durationMs - elapsed(timer, now));
}

export function progress(timer, now) {
  return timer.durationMs > 0 ? elapsed(timer, now) / timer.durationMs : 1;
}

export function start(timer, now) {
  if (timer.status !== STATUS.IDLE) return timer;
  return { ...timer, status: STATUS.RUNNING, startedAt: now, elapsedMs: 0 };
}

export function pause(timer, now) {
  if (timer.status !== STATUS.RUNNING) return timer;
  return {
    ...timer,
    status: STATUS.PAUSED,
    elapsedMs: elapsed(timer, now),
    startedAt: null,
    pauseCount: timer.pauseCount + 1,
  };
}

export function resume(timer, now) {
  if (timer.status !== STATUS.PAUSED) return timer;
  return { ...timer, status: STATUS.RUNNING, startedAt: now };
}

// Advances a running timer; flips it to complete once the time is up.
export function tick(timer, now) {
  if (timer.status !== STATUS.RUNNING) return timer;
  if (elapsed(timer, now) < timer.durationMs) return timer;
  return finish(timer, now, false);
}

// On-demand completion, used to test the end state without waiting.
export function completeNow(timer, now) {
  if (timer.status !== STATUS.RUNNING && timer.status !== STATUS.PAUSED) return timer;
  return finish(timer, now, true);
}

export function reset(timer, durationMs = timer.durationMs) {
  return createTimer(durationMs);
}

function finish(timer, now, forced) {
  return {
    ...timer,
    status: STATUS.COMPLETE,
    elapsedMs: timer.durationMs,
    startedAt: null,
    completedAt: now,
    forced,
  };
}

export function formatClock(ms) {
  const total = Math.ceil(ms / 1000);
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  const mm = String(m).padStart(2, '0');
  const ss = String(s).padStart(2, '0');
  return h > 0 ? `${h}:${mm}:${ss}` : `${mm}:${ss}`;
}
