# Focus Rooms — Game Design Document

> Focus for an hour. Earn coins. Turn an empty room into a home, then into a world.

## 1. Concept

The player starts with a bare, isometric room floating on a slab of grass and soil. Every completed one-hour focus session (a long-form Pomodoro) pays coins. Coins buy furniture, decor, tech, living things and land expansions. Along the way the player pins their own writing to the walls, and a journey of named stages unlocks new things to buy.

The room is a record of the hours the player has put in. Nothing in it can be bought with anything except focused time.

**Pillars**
- **Time is the only currency source.** No grinding, no ads. Coins come only from finished sessions.
- **Visible progress.** Every purchase changes the room right away. The four-stage reference image (empty room → workspace → lived-in → garden) is the intended arc.
- **Gentle, not punishing.** Giving up pays nothing but costs nothing. Pausing only forfeits a small bonus.
- **Personal.** Writings make each room the player's own.

---

## 2. Core mechanics

### 2.1 Focus timer → coins
| Rule | Value (tunable) |
|---|---|
| Session length | **60 minutes** |
| Base reward | **25 coins** per completed session |
| Unbroken Focus bonus | **+5 coins** if never paused |
| Give up (reset mid-session) | 0 coins, no penalty |
| Starting wallet | 40 coins (enough for the first desk and chair) |

- Coins are credited **once**, at the moment the timer reaches zero.
- The timer runs on wall-clock time. Closing or reloading the app does not lose a session. If it ran out while the player was away, it pays when they return.
- The player sees three clear phases: **Start** (ready), **Ongoing** (focusing or paused) and **Complete** (reward paid).

### 2.2 Room expansion
- **Placement.** Each item has a hand-designed spot, so the room always looks composed. Free placement is a stretch goal.
- **Dependencies.** Some items need others first: a computer needs a desk, a cat needs a cushion, a shelf needs a dresser, and the garden items need the Garden Plot.
- **Land expansion.** The **Garden Plot** adds a second island beside the room, as in the reference image. Paths, wildflowers and a pine grove then grow on it. Later expansions could add a porch, a pond or a second floor.

### 2.3 Journey progression
Stages unlock by **completed sessions**, not by coins, so spending never slows progress. Each stage pays a one-time arrival bonus and opens new shop items.

| # | Stage | Sessions | Bonus | Unlocks |
|---|---|---|---|---|
| 1 | The Empty Room | 0 | — | Desk, chair |
| 2 | First Desk | 1 | +10 | Rug, floor lamp, computer, desk lamp, window, clock, corkboard, fig plant |
| 3 | Making It Home | 3 | +20 | Dresser, ladder shelf, pegboard, framed print, cushion, cat, succulent |
| 4 | Cozy Nights | 6 | +30 | String lights, candle, neon strip |
| 5 | Breaking Ground | 10 | +40 | Garden Plot, stone path, wildflowers |
| 6 | The Grove | 15 | +50 | Pine grove |

### 2.4 Companion and living things
- **Biscuit the dog** is free from the start and mirrors the timer. Asleep = ready, sitting with a wagging tail = focusing, head tilted with "?" = paused, bouncing with hearts = complete.
- **Plants grow.** The fig gains a growth stage every two sessions after purchase, up to 2.
- **Cat.** Can be bought. Lives on the cushion and blinks at you.

### 2.5 Ambient feedback
- The **wall clock's red hand** shows how far through the hour you are (one full turn = one session).
- The monitor and lamps switch on while you focus.
- String lights glow, and a coin burst plays when a session completes.

---

## 3. Purchasable items

| Category | Items | Price range |
|---|---|---|
| **Furniture** | Oak desk, woven chair, striped rug, floor lamp, pet cushion, low dresser, ladder shelf | 15–60 |
| **Tech** | Desktop computer, desk lamp, neon strip | 15–40 |
| **Decor** | Window and blind, wall clock, corkboard, pegboard, framed print, candle, string lights | 10–45 |
| **Life** | Fiddle-leaf fig (grows), desk succulent, black cat | 10–80 |
| **Expansion** | Garden Plot, stone path, wildflowers, pine grove | 25–120 |

Pricing aims for roughly one meaningful purchase per session early on, and bigger goals (cat, garden) spread over several sessions later.

---

## 4. Writings

Writings let players leave their own words in the room.

| Type | How it works | Status |
|---|---|---|
| **Pinned notes** | Up to 6 notes of 80 characters or less on the corkboard, 2 coins each. Hover in the room to read. | Prototype |
| **Session log** | After a session, an optional one-line "what I did". Builds a journal of the journey. | Planned |
| **Framed quote** | One featured quote shown large on a frame. | Planned |
| **Chalkboard goals** | A weekly goal list. Ticking items off earns a small bonus. | Planned |
| **Journey milestones** | A short auto-written entry each time a stage is reached. | Planned |

Writings need the Corkboard. This makes "decorate the wall" the first step toward writing.

---

## 5. Progression flow

```
Open app ─▶ Empty room, 40 coins, dog asleep
   │
   ├─▶ Buy desk + chair (35)
   │
   └─▶ START 60-min focus ──▶ dog awake, screen/lamps on, clock hand sweeps
            │        ▲
          pause    resume          give up → back to start, 0 coins
            │        │
            ▼        │
         COMPLETE ◀── timer hits 0
            │
            ├─▶ +25 (+5 unbroken) coins, session count +1
            ├─▶ stage reached? → arrival bonus + new shop items
            ├─▶ plants grow
            ▼
         Shop / write notes ─▶ start next session ─▶ …
```

**Session-by-session target arc** (about 30 coins per session plus bonuses):
- **Sessions 1–2:** workspace (computer, lamp, rug, window).
- **Sessions 3–6:** home (storage, art, cushion, cat, corkboard notes).
- **Sessions 6–10:** cozy evenings (string lights, candle, neon).
- **Sessions 10–15+:** expand outside (garden, path, flowers, pine grove).

---

## 6. Future ideas
- Free placement and rotation of furniture. More rooms joined into a neighbourhood.
- Day/night cycle tied to real local time.
- Weekly streak bonuses, with the soft rule kept: no losses, only gains.
- Short breaks between sessions where the dog wants a walk (a 5-minute break timer).
- Shareable room snapshots.
