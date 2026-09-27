# Hostile reviewer checklist

## Category fit

- [ ] No frontend added.
- [ ] Main value remains reusable contract logic.
- [ ] Example consumer remains minimal and clearly secondary.

## Consensus correctness

- [ ] Leader result is not accepted on schema shape alone.
- [ ] Validator independently re-fetches all frozen sources.
- [ ] Validator independently re-runs semantic classification.
- [ ] Decision-bearing outcome must agree.
- [ ] Determinate evidence quote must exist in validator-rendered source.
- [ ] Source availability threshold is enforced programmatically.

## State integrity

- [ ] Consumer is immutable in the latch definition.
- [ ] Action hash is immutable.
- [ ] Definition hash matches off-chain preview.
- [ ] Only consumer can arm.
- [ ] Initiator can cancel only before arm.
- [ ] Terminal latch cannot be re-resolved.
- [ ] Expiry cannot commit.

## Liveness

- [ ] Inconclusive result leaves latch retryable.
- [ ] Unavailable sources leave latch retryable.
- [ ] Retry cooldown works.
- [ ] Attempt cap works.
- [ ] Expiry always reaches a terminal revert signal.

## Messaging

- [ ] Terminal callback uses finality.
- [ ] Consumer callback is idempotent.
- [ ] Wrong sender cannot commit/revert consumer state.
- [ ] Wrong definition/action hash cannot apply.
- [ ] Callback retry works after failed/non-acknowledged delivery.
- [ ] Consumer acknowledgement is recorded separately.

## Live evidence

- [ ] RPC verified as chain 61999 before deploy.
- [ ] Both deployment receipts finalized.
- [ ] At least one true commit lifecycle finalized.
- [ ] At least one semantic failure lifecycle finalized.
- [ ] At least one inconclusive/retry lifecycle finalized.
- [ ] At least one expiry lifecycle finalized.
- [ ] Contract source fetched from deployment matches repository source hash.
