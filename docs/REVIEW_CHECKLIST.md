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
- [x] Determinate evidence quote must exist in validator-rendered source.
- [x] Source availability threshold is enforced programmatically.

## State integrity

- [x] Consumer is immutable in the latch definition.
- [x] Action hash is immutable.
- [x] Definition hash matches off-chain preview.
- [x] Only consumer can arm.
- [x] Initiator can cancel only before arm.
- [x] Terminal latch cannot be re-resolved.
- [x] Expiry cannot commit.

## Liveness

- [x] Inconclusive result leaves latch retryable.
- [x] Unavailable sources leave latch retryable.
- [x] Retry cooldown works.
- [x] Attempt cap works.
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
- [x] At least one inconclusive/retry lifecycle finalized.
- [x] At least one expiry lifecycle finalized.
- [x] Contract source fetched from deployment matches repository source hash.

Transaction hashes, deployed addresses, exact source hashes and state read-backs are recorded in [DEPLOYMENT.md](../DEPLOYMENT.md).
