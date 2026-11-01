# Focus, accountability and social mechanics

**Design proposal — no timer, multiplayer, wallet or board service is implemented in this checkout.** This document turns the product direction into implementable responsibilities without describing them as shipped features.

## The work session

A builder enters a café room, chooses a seat/work station, writes an intention and selects a duration. Example presets could be 25 and 50 minutes, plus a user-defined block; these are suggested defaults. A short confirmation sets the start/end timestamps. The avatar may become seated and the UI quiet during focus. Existing Sit/Wave clips are available assets, not integrated station interactions.

Use explicit states: `draft → running → completed` or `draft/running → cancelled`. A break is a separate state/session segment. Decide whether pause is allowed before implementation; paused time must never silently count toward earned focus. Reconnect should recover the server session, not create a second block. Explain what “completed” means and ask for an optional outcome note.

For a local prototype, persist an intention and wall-clock end time with a clear local-only label. For shared sessions and rewards, use server timestamps; client countdown displays an estimate and resynchronizes. A hidden/background browser tab should not stop a timer simply because rendering is throttled.

## Parallel work and accountability

Presence says who is in the room, not whether their work is productive. Publish a minimal opt-in state: display name/avatar, available/focusing/on break/presenting and, if the person chooses, the session goal or remaining time. Do not infer productivity by watching keystrokes, reading a builder's editor or exposing their private project.

A proposed network contract includes joining/leaving a room, heartbeat/expiry, session-state updates and resynchronization after reconnect. A missed heartbeat should become stale/offline, not remain “focusing” forever. The server checks room membership and ownership of updates. Clients can smooth avatar movement locally while receiving authoritative room state.

The exact backend/provider is undecided. A practical design separates the Unity/WebGL client from authenticated HTTP endpoints for persisted operations and a real-time channel for room presence. The static website currently serves assets only; it is not a multiplayer server.

## Rewards and social currency

Completing an eligible block is intended to grant both coins and XP. Coins can fund café expression; XP can represent accumulated contribution, reputation or unlocks. Whether XP itself can be spent remains an explicit product decision. Document the chosen behavior before implementing it.

Examples to evaluate: a cosmetic coffee, desk decoration, supportive “cheer,” a shared break celebration, or a showcase opportunity. These are social uses, not cash redemption. Prices, reward quantities, minimum durations and daily caps are not finalized.

Reward grants must be based on eligible session completion, not a client calling “add coins.” Proposed records:

- `FocusSession`: owner, room, intention visibility, startedAt, endsAt, state and completion outcome.
- `RewardTransaction`: immutable ID, owner, session ID, reward type, amount, reason and timestamp.
- `CatalogItem` and `SpendTransaction`: item/version, cost, owner and an idempotency key.

Enforce one completion grant per session/reward type in the database and commit the completion plus grants atomically. Retries return the existing result. A spend checks balance and writes its debit atomically. XP or coin values in the UI are views of persisted transactions, not trusted local variables.

Acceptance checks: duplicate complete requests grant once; cancelled/ineligible blocks earn no completion grant; reconnect shows the same balance; double-clicking Spend debits once; simultaneous requests cannot overspend; one account cannot alter another's session. This is honest completion tracking, not proof that a builder actually worked.

## Builder showcase board

The board is a public-facing gallery within the café. The first implementation should support a title, short summary, creator, optional project URL, milestone, created/updated timestamps and visibility choice. Detail cards can invite feedback or a demo during a break. A later presentation entity can add a room/time slot, speaker and attendance action.

Open the board through a clearly marked café object and provide an equivalent accessible UI control. Keep text as data so it can be edited, searched and moderated. The current decorative signs are visual props, not a functioning board.

Posting should be intentional. A focus intention does not automatically become a public post. Include ownership checks, edit/delete, reporting, link validation and safe text rendering. Give a clear distinction between a public showcase and a room-only message. Avoid presenting a room as private if posts are readable publicly.

Acceptance checks: a post survives reload; a second account can see an allowed public post; only its owner/moderator can edit it; deletion removes it from the board; untrusted text cannot execute script; external links are explicit and safe; cancelling a presentation does not leave a live slot.

## Keeping the café useful

Make the timer and remaining time legible without covering the scene. Respect sound/blur choices. Place celebrations and social prompts at natural boundaries, not in the middle of deep work. Reward consistency and helpful sharing; validate reward design with builders before adding a competitive leaderboard.

Implementation of these services should include tests and an update to [FEATURE_STATUS.md](FEATURE_STATUS.md). Documentation alone does not make a feature shipped.
