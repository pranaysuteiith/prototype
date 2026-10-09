# Focus Rooms — Prototype Specification

A playable, testable prototype of the Pomodoro room-builder. It covers the timer, coin rewards, on-demand completion, the three timer phases, the character assets and the progression loop.

## Chosen inputs

| Input | Value |
|---|---|
| Target platform | Web browser (desktop and mobile) |
| Language | JavaScript (ES modules), HTML, CSS |
| Framework / engine | None. Plain DOM and inline SVG, no build step |
| `pomodoro_duration_minutes` | 60 (dev panel: 5 min, 1 min, 10 s) |
| `coin_reward_per_pomodoro` | 25 (+5 if never paused) |
| `on_demand_complete_command` | **Complete now** button, the `C` key, or `focusRooms.completeNow()` in the console |
| `test_scenarios` | See [Test plan](#test-plan) |
| Assets | Biscuit the dog, a black cat, fig plant, succulent, pine trees, wildflowers, plus furniture. All are procedural SVG, so no image files are needed. |

All balance values live in `src/config.js`, `src/core/catalog.js` and `src/core/journey.js`.

---

## Architecture

```
┌──────────────────────── browser ────────────────────────┐
│ index.html + styles.css                                  │
│                                                          │
│  src/ui/app.js   ── dispatch(action) ──▶  src/core/game.js│
│   (DOM, input,                              reduce()      │
│    250 ms tick,  ◀──── new state ───────   │  uses:       │
│    save, toasts)                           │  timer.js    │
│        │                                   │  economy.js  │
│        ▼                                   │  catalog.js  │
│  src/ui/room.js ── iso.js, assets.js       │  journey.js  │
│   (state → SVG string)                                    │
│        │                                                  │
│  src/core/storage.js ⇄ localStorage (guarded)             │
└──────────────────────────────────────────────────────────┘
```

- **Pure core.** Everything in `src/core` is plain functions. They take `now` as an argument and never read the clock, the DOM or storage. That makes every rule unit-testable in Node.
- **Single reducer.** `reduce(state, action, now)` is the only way state changes. The UI turns the reducer's `log` entries into toasts.
- **Pay once.** Coins are paid in one place, `withTimer()`. Payment happens when a timer transition changes the status from not-complete to complete. Ticks or completion calls after that cannot pay twice.
- **Wall-clock timer.** The timer stores `startedAt` and banked `elapsedMs`. Reloads and background tabs keep the correct time, and a session that ended while the app was closed pays out on the next tick.
- **Renderer.** `renderRoom(state)` turns state into one SVG string. The app only re-renders when `roomKey(state)` changes (purchases, notes, timer status, plant growth). The clock hand is updated in place every tick.

---

## Data models

```js
// Timer (src/core/timer.js)
{
  status: 'idle' | 'running' | 'paused' | 'complete',
  durationMs: 3_600_000,
  startedAt: number | null,   // wall clock of the current running stretch
  elapsedMs: number,          // time banked before that stretch
  pauseCount: number,         // > 0 forfeits the unbroken bonus
  completedAt: number | null,
  forced: boolean,            // finished via completeNow
}

// Game (src/core/game.js), persisted without `log`
{
  version: 1,
  coins: number,
  lifetimeCoins: number,
  sessionsCompleted: number,
  stageReached: number,                       // index into STAGES
  owned: { [itemId]: { boughtAtSession } },   // drives growth
  notes: [{ id, text, color }],               // max 6, ≤ 80 chars
  timer: Timer,
  log: [{ id, kind, text }],                  // UI toasts, last 30
  nextId: number,
}

// Catalog item (src/core/catalog.js)
{ id, name, category: 'furniture'|'tech'|'decor'|'life'|'expansion',
  price, stage, requires?: [itemId], description }

// Journey stage (src/core/journey.js)
{ name, sessions, bonus, blurb }
```

**Actions:** `timer/start`, `timer/pause`, `timer/resume`, `timer/tick`, `timer/completeNow`, `timer/reset`, `timer/setDuration` (idle only), `shop/buy {itemId}`, `notes/add {text}`, `notes/remove {id}`, `debug/grantCoins {amount}`.

---

## State machine

```
                 start                  pause
   ┌──────┐  ───────────▶  ┌─────────┐ ───────▶ ┌────────┐
   │ IDLE │                │ RUNNING │          │ PAUSED │
   └──────┘  ◀─ reset ───  └─────────┘ ◀─────── └────────┘
      ▲                      │     │    resume      │
      │                 tick │     │ completeNow    │ completeNow
      │          (time up)   ▼     ▼                ▼
      │                   ┌──────────┐
      └────── reset ───── │ COMPLETE │  ← coins paid exactly once here
                          └──────────┘
```

| UI phase | Statuses | Badge | Dog | Buttons |
|---|---|---|---|---|
| **Start** | idle | Ready to start | Asleep, "Zzz" | Start focus |
| **Ongoing** | running | Focusing (green) | Sitting, tail wagging | Pause · Give up |
| **Ongoing** | paused | Paused (amber), dimmed clock | Head tilt, "?" | Resume · Give up |
| **Complete** | complete | Complete (orange) | Bouncing, hearts | Start next session |

Invalid transitions (for example pausing while idle, or completing a session that never started) return the same state object. That makes them no-ops.

---

## UI layout

```
┌──────────────────────────────────────────────────────────────┐
│ ▣ Focus Rooms                              (●40) (3 sessions)│
├──────────────────────────────────────┬───────────────────────┤
│ STAGE 2 OF 6                  blurb  │ [FOCUSING]   Earn 25+5│
│ First Desk                           │  42:17                │
│                                      │  ▓▓▓▓▓▓▓░░░░░░░       │
│        isometric room (SVG)          │ [ Pause ] [ Give up ] │
│     walls · floor · items · dog      │ Biscuit is keeping…   │
│     garden island when expanded      ├───────────────────────┤
│                                      │ Journey  ▓▓▓░  stages │
│            (+30 coin burst)          ├───────────────────────┤
│                                      │ Shop [Furn|Tech|…]    │
│                                      │  item · desc · (●25)  │
│                                      ├───────────────────────┤
│                                      │ Writings  [note][Pin] │
│                                      ├───────────────────────┤
│                                      │ Dev tools (dashed)    │
└──────────────────────────────────────┴───────────────────────┘
```
Below 980px the room stacks above the sidebar. The page works at 390px width with no horizontal scroll. Light and dark themes follow the OS. Animations respect `prefers-reduced-motion`.

---

## Code scaffold

```
index.html              page shell and sidebar markup
styles.css              theme tokens, layout, SVG character animations
package.json            npm start (static server), npm test (node --test)
scripts/serve.js        zero-dependency static file server
src/config.js           duration, reward, bonus, note cost, debug flag
src/core/timer.js       pure Pomodoro state machine + formatting
src/core/catalog.js     item definitions (price, stage gate, requirements)
src/core/journey.js     stages, stageFor(), progressToNext()
src/core/economy.js     rewardFor(), purchaseCheck()
src/core/game.js        game state + reduce(); notes; plant growth
src/core/storage.js     guarded save/load through any Storage-like object
src/ui/iso.js           isometric projection, cuboids, wall/floor planes
src/ui/assets.js        dog (4 moods) and cat sprites
src/ui/room.js          scene composition: slab, walls, items, garden
src/ui/app.js           DOM wiring, tick loop, toasts, keyboard, dev tools
tests/*.test.js         timer, game rules, storage, renderer
docs/                   this spec, the game design doc, the source prompt
```

### Asset references
All art is drawn in code as SVG, so it stays sharp at any size and needs no files to download.

| Asset | Where | Notes |
|---|---|---|
| Biscuit (dog) | `assets.js → dog(mood)` | `sleep`, `focus`, `curious`, `celebrate` |
| Cat | `assets.js → cat()` | blinking eyes, swaying tail |
| Fig plant | `room.js → plant(growth)` | 3 growth stages |
| Pines, wildflowers, pebbles | `room.js → garden()` | seeded random, so they look the same on every render |
| Furniture | `room.js` | built from `iso.box()` cuboids plus flat details on `planeX/Y/Z` |

To replace the placeholder art with illustrated sprites, keep the function signatures and return `<image href="…">` from them.

---

## Test plan

Run `npm test` (Node ≥ 18, no dependencies).

| Area | Case | File |
|---|---|---|
| Timer | New timer is in the Start phase with 60:00 left | `timer.test.js` |
| Timer | Start → Ongoing; countdown follows the injected clock | `timer.test.js` |
| Timer | Pause freezes the time; resume continues | `timer.test.js` |
| Timer | Tick completes exactly at zero (not 1 ms early) | `timer.test.js` |
| Timer | Overdue running timer completes on next tick | `timer.test.js` |
| Timer | **completeNow** finishes running *and* paused timers, `forced=true` | `timer.test.js` |
| Timer | Invalid transitions are no-ops (incl. completeNow from idle) | `timer.test.js` |
| Timer | Reset returns to Start from every state | `timer.test.js` |
| Coins | Unbroken session pays 25 + 5 | `game.test.js` |
| Coins | Paused session pays 25 | `game.test.js` |
| Coins | On-demand completion pays like a real session | `game.test.js` |
| Coins | Repeated ticks or completes never pay twice | `game.test.js` |
| Coins | Giving up pays 0 | `game.test.js` |
| Shop | Starting coins buy desk + chair | `game.test.js` |
| Shop | Price, stage lock, requirements, owned and unknown are rejected | `game.test.js` |
| Shop | Every catalog item is reachable | `game.test.js` |
| Journey | Stage thresholds; bonuses paid once each over 15 sessions | `game.test.js` |
| Writings | Needs corkboard, costs 2, trims, rejects empty or long, max 6 | `game.test.js` |
| Life | Plant grows every 2 sessions, capped | `game.test.js` |
| Save | Round-trip incl. a running timer; corrupt, blocked or old saves start fresh | `storage.test.js` |
| Render | Empty and fully furnished rooms render without NaN | `room.test.js` |
| Render | Dog pose matches every timer state | `room.test.js` |
| Render | Note text is XML-escaped | `room.test.js` |

**Manual checks**
1. `npm start` and open http://localhost:5173. Buy the desk and chair, then press **Start focus**.
2. Press **Complete now** or `C`. You should see the badge change to Complete, a +40 coin burst (30 + 10 stage bonus), the dog bouncing, and "First Desk" reached.
3. Set **Session length → 10 sec**, start, and reload the page mid-session. It should keep counting and pay at zero by itself.
4. Pause, then complete. The reward should be 25 with no bonus.
5. Give up mid-session. You should see a toast and get no coins.
6. Add `?debug=0` to the URL to hide the dev tools.
