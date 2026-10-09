// The journey: named stages unlocked by completed focus sessions. Each stage
// opens new catalog items and pays a one-time arrival bonus.

export const STAGES = [
  { name: 'The Empty Room', sessions: 0, bonus: 0, blurb: 'Bare walls, bare floor. Buy a desk and chair, then start your first hour.' },
  { name: 'First Desk', sessions: 1, bonus: 10, blurb: 'A workspace takes shape. Light, tech and a first plant are in the shop.' },
  { name: 'Making It Home', sessions: 3, bonus: 20, blurb: 'Storage, art, and maybe a cat who will take over the cushion.' },
  { name: 'Cozy Nights', sessions: 6, bonus: 30, blurb: 'String lights, candles and neon for the long evenings.' },
  { name: 'Breaking Ground', sessions: 10, bonus: 40, blurb: 'The room is full. Time to expand outside.' },
  { name: 'The Grove', sessions: 15, bonus: 50, blurb: 'Plant a forest. Keep going: every hour still pays.' },
];

export function stageFor(sessionsCompleted) {
  let index = 0;
  for (let i = 0; i < STAGES.length; i++) {
    if (sessionsCompleted >= STAGES[i].sessions) index = i;
  }
  return index;
}

// { current, next, done, needed } for the progress bar toward the next stage.
export function progressToNext(sessionsCompleted) {
  const current = stageFor(sessionsCompleted);
  const next = STAGES[current + 1];
  if (!next) return { current, next: null, done: 1, needed: 1 };
  const base = STAGES[current].sessions;
  return { current, next: current + 1, done: sessionsCompleted - base, needed: next.sessions - base };
}
