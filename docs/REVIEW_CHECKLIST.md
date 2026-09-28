# Hostile reviewer checklist

## Category fit

- [x] No frontend added.
- [x] Main value remains reusable contract logic.
- [x] Example consumer remains minimal and clearly secondary.

## Consensus correctness

- [x] Leader result is not accepted on schema shape alone.
- [x] Validator independently re-fetches all frozen sources.
- [x] Validator independently re-runs semantic classification.
- [x] Decision-bearing outcome must agree.
- [x] Determinate leader quote must exist verbatim in the validator's independent source fetch; validator separately asks whether that exact quote materially supports its independently classified outcome.
- [x] Stored `available_mask` is explicitly leader-observation metadata; consensus binds the availability threshold and outcome, not an exact per-source bitmap.
- [x] Source availability threshold is enforced programmatically.

## State integrity

- [x] Consumer is immutable in the latch definition.
- [x] Action hash is immutable.
- [x] Definition hash matches off-chain preview.
- [x] Only consumer can arm.
- [x] Initiator can cancel only before arm.
- [x] Consumer can retry a bounded arm while the exact latch remains CREATED; exact hash-bound cancellation status lets it clear a cancelled provisional grant without creating usable credit.
- [x] Consumer cannot locally alter a grant when its exact latch is ARMED or terminal.
- [x] Terminal latch cannot be re-resolved.
- [x] Expiry cannot commit.

## Liveness

- [x] Inconclusive result leaves latch retryable.
- [x] Unavailable sources leave latch retryable.
- [x] Retry cooldown works.
- [x] Attempt cap is explicitly exhausted by repeated INCONCLUSIVE attempts; further resolution is rejected and expiry still fails closed.
- [x] Expiry always reaches a terminal revert signal.

## Messaging

- [x] Terminal callback uses finality.
- [x] Consumer callback is idempotent.
- [x] Wrong sender cannot commit/revert consumer state.
- [x] Wrong definition/action hash cannot apply.
- [x] Callback retry is bounded while acknowledgement is absent; an actual failed child was not fabricated.
- [x] Consumer acknowledgement is recorded separately.

## Live evidence

- [x] RPC verified as chain 61999 before each deployment and live-test phase.
- [x] Both deployment receipts finalized.
- [x] At least one true commit lifecycle finalized.
- [x] At least one semantic failure lifecycle finalized.
- [ ] Inconclusive/retry lifecycle finalized live (Direct Mode coverage exists).
- [ ] Expiry lifecycle finalized live (Direct Mode coverage exists).
- [x] Contract source fetched from deployment contains the complete repository source byte-for-byte; local source hashes are recorded.

Transaction hashes, deployed addresses, exact source hashes and state read-backs are recorded in [DEPLOYMENT.md](../DEPLOYMENT.md).
