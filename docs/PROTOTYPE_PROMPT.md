# Prototype prompt (filled in)

The original brief left `[FILL]` placeholders and ended mid-sentence under *Constraints*. This is the same brief with the values used to build this repo filled in. You can paste it into a model to regenerate or extend the prototype.

---

**Role.** You are an experienced game developer and systems designer.

**Task.** Build a playable, testable prototype of a Pomodoro-based room-building game:
- A Pomodoro timer with **start, pause, resume, give up, and on-demand complete**. The on-demand complete is for testing the end state without waiting.
- **Coins** for each completed pomodoro, with a running total.
- Three player-visible **timer phases**: start (idle), ongoing (running or paused), complete.
- **Character and life assets**: a companion dog that reacts to each phase, plus a cat, plants, trees and flowers, drawn as simple placeholder art.
- Coins **buy furniture and decor** that appear in an isometric room. A **journey** of stages, unlocked by completed sessions, gates the shop. Players can **pin short writings** to the wall.

**Inputs**
- Target platform: web browser (desktop and mobile)
- Language: JavaScript (ES modules), HTML, CSS
- Framework: none. Plain DOM and inline SVG, no build step
- pomodoro_duration_minutes: 60 (with dev overrides of 5 min, 1 min and 10 s)
- coin_reward_per_pomodoro: 25, plus 5 if the session was never paused
- on_demand_complete_command: a "Complete now" button, the `C` key, and `focusRooms.completeNow()` in the console
- test_scenarios: timer transitions and invalid transitions; pay-exactly-once; pause bonus; give-up pays nothing; shop gating; journey bonuses; notes validation; save/load including a running timer; renderer output for every dog mood
- asset_descriptions: dog (asleep / focused / curious / celebrating), cat, fiddle-leaf fig with growth stages, succulent, pine trees, wildflowers, furniture

**Deliver**
An architecture overview, data models, the state machine, UI layout sketches, a code scaffold (file tree with a short description of each file), asset references, a test plan with example test cases, and the working code.

**Constraints**
- Keep the core requirements: Pomodoro timer, coin rewards, on-demand finish, visible timer states, character assets.
- Do not add domain facts beyond the stated inputs.
- Do not translate or change any mixed-language content.
- Do not leave out the on-demand complete feature.
- Do not award coins twice for one session, or for an abandoned session.

Where each part lives in this repo: `docs/PROTOTYPE_SPEC.md` (spec), `docs/GAME_DESIGN.md` (design), `src/` (code), `tests/` (tests).
