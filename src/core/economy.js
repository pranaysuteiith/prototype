import { CONFIG } from '../config.js';
import { getItem } from './catalog.js';

// Coins paid for a finished timer. Forced completions (dev "Complete now")
// pay the same as a real session so the full loop can be tested quickly.
export function rewardFor(timer, config = CONFIG) {
  const base = config.coinsPerPomodoro;
  const bonus = timer.pauseCount === 0 ? config.unbrokenFocusBonus : 0;
  return { base, bonus, total: base + bonus };
}

// Why an item can or cannot be bought right now. `reason` is null when it can.
export function purchaseCheck(state, itemId) {
  const item = getItem(itemId);
  if (!item) return { ok: false, reason: 'Unknown item' };
  if (state.owned[itemId]) return { ok: false, reason: 'Owned' };
  if (item.stage > state.stageReached) return { ok: false, reason: 'Locked' };
  const missing = (item.requires || []).filter((id) => !state.owned[id]);
  if (missing.length) {
    return { ok: false, reason: `Needs ${missing.map((id) => getItem(id).name).join(', ')}` };
  }
  if (state.coins < item.price) return { ok: false, reason: 'Not enough coins' };
  return { ok: true, reason: null };
}
