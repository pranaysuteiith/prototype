import { CONFIG } from '../config.js';
import { createGame } from './game.js';

// Save/load through any Storage-like object (localStorage in the browser, a
// Map-backed stub in tests). Storage can be missing or throw (private mode,
// blocked site data), so every access is guarded and the game still runs.

export function loadGame(storage, config = CONFIG) {
  const fresh = createGame(config);
  try {
    const raw = storage?.getItem(config.saveKey);
    if (!raw) return fresh;
    const saved = JSON.parse(raw);
    if (saved?.version !== fresh.version) return fresh;
    // Merge so fields added in later builds get their defaults.
    return { ...fresh, ...saved, timer: { ...fresh.timer, ...saved.timer }, log: [] };
  } catch {
    return fresh;
  }
}

export function saveGame(storage, state, config = CONFIG) {
  try {
    const { log, ...persisted } = state;
    storage?.setItem(config.saveKey, JSON.stringify(persisted));
    return true;
  } catch {
    return false;
  }
}

export function clearSave(storage, config = CONFIG) {
  try {
    storage?.removeItem(config.saveKey);
  } catch {
    /* nothing to clear */
  }
}
