import assert from 'node:assert/strict';
import { test } from 'node:test';
import * as T from '../src/core/timer.js';

const MIN = 60_000;
const HOUR = 60 * MIN;

test('a new timer is in the start phase with the full duration remaining', () => {
  const t = T.createTimer(HOUR);
  assert.equal(t.status, T.STATUS.IDLE);
  assert.equal(T.phaseOf(t), T.PHASE.START);
  assert.equal(T.remaining(t, 0), HOUR);
  assert.equal(T.formatClock(T.remaining(t, 0)), '1:00:00');
});

test('start → ongoing, counts down against the injected clock', () => {
  const t = T.start(T.createTimer(HOUR), 1000);
  assert.equal(T.phaseOf(t), T.PHASE.ONGOING);
  assert.equal(T.remaining(t, 1000 + 10 * MIN), 50 * MIN);
  assert.equal(T.formatClock(T.remaining(t, 1000 + 10 * MIN)), '50:00');
  assert.equal(T.progress(t, 1000 + 30 * MIN), 0.5);
});

test('pause freezes the clock; resume continues from where it stopped', () => {
  let t = T.start(T.createTimer(HOUR), 0);
  t = T.pause(t, 20 * MIN);
  assert.equal(t.status, T.STATUS.PAUSED);
  assert.equal(T.phaseOf(t), T.PHASE.ONGOING);
  assert.equal(t.pauseCount, 1);
  assert.equal(T.remaining(t, 999 * MIN), 40 * MIN, 'time does not pass while paused');
  t = T.resume(t, 100 * MIN);
  assert.equal(T.remaining(t, 110 * MIN), 30 * MIN);
});

test('tick completes the timer exactly when time runs out', () => {
  let t = T.start(T.createTimer(HOUR), 0);
  assert.equal(T.tick(t, HOUR - 1), t, 'still running one ms early');
  t = T.tick(t, HOUR);
  assert.equal(t.status, T.STATUS.COMPLETE);
  assert.equal(T.phaseOf(t), T.PHASE.COMPLETE);
  assert.equal(t.forced, false);
  assert.equal(T.remaining(t, HOUR), 0);
});

test('a timer left running past its end completes on the next tick', () => {
  const t = T.tick(T.start(T.createTimer(HOUR), 0), 5 * HOUR);
  assert.equal(t.status, T.STATUS.COMPLETE);
});

test('completeNow finishes a running or paused timer on demand', () => {
  const running = T.completeNow(T.start(T.createTimer(HOUR), 0), 5 * MIN);
  assert.equal(running.status, T.STATUS.COMPLETE);
  assert.equal(running.forced, true);
  assert.equal(running.completedAt, 5 * MIN);

  const paused = T.completeNow(T.pause(T.start(T.createTimer(HOUR), 0), MIN), 2 * MIN);
  assert.equal(paused.status, T.STATUS.COMPLETE);
});

test('invalid transitions are no-ops', () => {
  const idle = T.createTimer(HOUR);
  assert.equal(T.pause(idle, 0), idle);
  assert.equal(T.resume(idle, 0), idle);
  assert.equal(T.completeNow(idle, 0), idle, 'cannot complete a session that never started');
  assert.equal(T.tick(idle, HOUR * 2), idle);

  const running = T.start(idle, 0);
  assert.equal(T.start(running, 10), running);
  assert.equal(T.resume(running, 10), running);

  const done = T.completeNow(running, 10);
  assert.equal(T.completeNow(done, 20), done);
  assert.equal(T.pause(done, 20), done);
  assert.equal(T.start(done, 20), done, 'must reset before starting again');
});

test('reset returns to the start phase from any state', () => {
  for (const t of [T.start(T.createTimer(HOUR), 0), T.completeNow(T.start(T.createTimer(HOUR), 0), 1)]) {
    const r = T.reset(t);
    assert.equal(r.status, T.STATUS.IDLE);
    assert.equal(r.durationMs, HOUR);
    assert.equal(r.pauseCount, 0);
  }
});
