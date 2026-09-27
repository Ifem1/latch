# Reviewer evidence ledger

This document is intentionally split into **already verifiable from source** and **must still be proven live**.

## Verifiable from this repository

- Contract-only submission, no frontend.
- Main primitive in `contracts/latch.py`.
- Separate minimal consumer in `contracts/example_consumer.py`.
- Immutable definition hash binds consumer, action, evidence surface and timing.
- Only bound consumer can arm.
- Custom `run_nondet_unsafe` validator independently re-observes evidence.
- Minimum-source availability is enforced before semantic judgement.
- Determinate outcomes require grounded verbatim evidence.
- Inconclusive/unavailable observations do not terminally settle.
- Deadline fails closed to `REVERT_REQUIRED`.
- Consumer callbacks and acknowledgements are finalized messages.
- Callback delivery state is distinct from semantic resolution state.
- Direct Mode suite includes 26 scenarios in `tests/direct/test_latch.py` (latest run: 26 passed).
- `python scripts/preflight.py`: PASS.
- GenVM lint and semantic validation pass for both contracts with GenVM `v0.2.16` and `genvm-linter` `0.11.0`.
- Stable GenLayer CLI reports `0.39.1`; the repository remains configured for stable Studionet.
- Source sizes are 42,423 bytes for LATCH and 11,104 bytes for ExampleLatchedGrant.

## Must be completed by final connected agent

| Evidence | Status |
|---|---|
| Direct Mode full run | PASS — 26 passed |
| GenVM lint on both contracts | PASS — lint and validation |
| RPC chain guard | PASS — canonical RPC returned chain ID 61999 |
| LATCH deployment to 61999 | PENDING |
| Consumer deployment to 61999 | PENDING |
| Live SATISFIED consensus | PENDING |
| Live FAILED consensus | PENDING |
| Live INCONCLUSIVE then retry | PENDING |
| Live expiry fail-closed | PENDING |
| Live callback acknowledgement | PENDING |
| Deployed-code/source hash match | PENDING |
| Finalized tx links recorded | PENDING |

No `PENDING` item should be rewritten as complete without actual evidence.
