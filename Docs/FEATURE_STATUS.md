# Feature status and roadmap

Status reviewed against source and saved evidence on 1 November 2026. “Implemented” means code/assets are present; historical validation is described separately in [VERIFICATION.md](VERIFICATION.md).

## Implemented prototype

- Painted café/crossroads environment, static people, props and vegetation.
- Green-sweater boy with keyboard locomotion, turning, walk/idle transitions and CharacterController gravity/collision.
- Camera follow, WASD panning, Q/E orbit, mouse dragging and wheel zoom.
- Simplified focus proxies, center-ray autofocus and toggleable URP depth of field.
- Park birds/ambience, occasional distant bark, volume/mute controls.
- Looping white-dress dancer near the café sign/traffic signal.
- WebGL game shell with welcome/loading/error UI, fullscreen and share-link action.
- Blender masters, exported FBXs, rig/actions, preview renders and validation records.

## Designed, not implemented

- Focus intention entry and a time-block timer.
- Persisted focus history and completion check-ins.
- Authentication, live room membership and synchronized builder presence.
- Real-time accountability status and shared breaks.
- Coin/XP reward balances, reward ledger and spending catalog.
- Public project showcase posts and presentation scheduling.
- Shared chat, moderation/reporting and cross-device identity.

No NPC, moving dancer or local avatar should be advertised as another live builder. No existing pickup tutorial object should be presented as a finished coin/XP economy.

## Proposed delivery sequence

1. **Focus MVP:** local timer and intention UI, interruption/cancel behavior, explicit completion. Persist locally; label local-only. Test background-tab behavior using timestamps rather than decrementing one second per rendered frame.
2. **Shared café:** authentication, rooms, reconnect/expiry and opt-in presence. Test two separate accounts/browsers and dropped connections.
3. **Rewards:** server-owned eligible completion and exactly-once grant, auditable balances and catalog debits. Test duplicate completion, retries and simultaneous requests.
4. **Showcase board:** opt-in posts, edit/delete, safe external links and an accessible list/detail UI connected to a café object.
5. **Presentations and social expression:** scheduled slots, supportive reactions and cosmetics. Validate whether these reinforce focus rather than interrupt it.

These are proposed milestones, not release commitments. Mobile performance, Godot/Babylon migration, new animations and vendor-generated asset pipelines need independent validation.
