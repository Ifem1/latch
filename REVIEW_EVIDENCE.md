# Reviewer evidence ledger

This ledger records checks that can be reproduced from source, finalized Studionet transactions, and read-back contract state. Full transaction IDs, addresses, outcomes, source hashes, and fee limitations are in [DEPLOYMENT.md](DEPLOYMENT.md).

## Submission shape

- Category: **Intelligent Contracts**.
- Standalone reusable LATCH primitive in `contracts/latch.py`; no frontend.
- Separate minimal cooperating consumer in `contracts/example_consumer.py`.
- Frozen definition/action binding, consumer-only arming, validator re-observation, grounded determinate evidence, availability threshold, bounded retry rules, fail-closed expiry, finalized child callbacks, idempotent handler and separately tracked acknowledgement.
- The example controls only cooperating provisional contract state; it makes no claim to reverse arbitrary external effects.

## Local verification

| Check | Result |
|---|---|
| Stable CLI / network configuration | CLI `0.39.1`; stable `studionet`; target chain 61999 |
| `python scripts/preflight.py` | PASS |
| `python scripts/source_manifest.py` | PASS |
| `python -m pytest tests/direct -v` | PASS — 30 scenarios |
| GenVM lint + semantic validation, LATCH | PASS — GenVM `v0.2.16`, linter `0.11.0`, 14 methods |
| GenVM lint + semantic validation, consumer | PASS — GenVM `v0.2.16`, linter `0.11.0`, 6 methods |
| RPC guard | Repeatedly returned `61999` from `https://studio.genlayer.com/api` before each live deployment/testing phase |

## Live deployed source

| Contract | Address | Deployment tx | SHA-256 | Exact fetched-source comparison |
|---|---|---|---|---|
| LATCH | `0x8BC6278e19CB5c40DDcBDb7c3Dc8fCbEDdd2096C` | `0x67da2b39085c1532db75069e0e9ede473272a1b08cc59eb876189216c7e4bb5c` | `07f08b6b4d79835abbb0b7275d674667c52a23a8dbb2090f68d5ac60f85dce9d` | `gen_getContractCode` bytes exactly match `contracts/latch.py` |
| ExampleLatchedGrant | `0xf4eCC1CD4A811C37fA31669aFd8fA238a1fc8C93` | `0xd6f64aff7f5586d6448790f95c14a36b22a46484a2f1b29dfef68b240cfc5987` | `81609ff0b41c51f0da7eac4ebffa810f7a1b23d59c3f4f76e9a1d5ff65b8be27` | `gen_getContractCode` bytes exactly match `contracts/example_consumer.py` |

Deployment source commit: `c7fe053735a2d78b2a446d832709d7e6abf529bd`. No contract source changes followed deployment.

## Live semantic results

| Scenario | Finalized and read-back result |
|---|---|
| SATISFIED | Latch 1 `COMMITTED`; attempt outcome and verbatim source excerpt recorded; finalized consumer callback; grant `COMMITTED`; usable credit 0→100; acknowledgement `COMMITTED`. |
| FAILED | Latch 2 `REVERT_REQUIRED`; outcome `FAILED`; finalized revert callback; grant `REVERTED`; usable credit unchanged at 100; acknowledgement `REVERTED`. |
| Insufficient sources | Latch 3 attempt 3 `UNAVAILABLE`; availability mask `10`; one of two required sources available; latch remains `ARMED`; callback count 0; grant remains provisional. |
| INCONCLUSIVE | Latch 4 attempt 4 `INCONCLUSIVE`, terminal false; latch remains `ARMED`, callback count 0. |
| Retry | Same frozen URL was later updated in public commit `fcf20ee`; after cooldown, latch 4 attempt 5 `SATISFIED`, terminal true; finalized commit callback; acknowledgement `COMMITTED`. The earlier PENDING revision remains in history. |
| Expiry | Latch 5 expired after its on-chain deadline; `REVERT_REQUIRED`; finalized consumer revert and acknowledgement; grant `REVERTED`; no credit was added. |

All public lifecycle fixtures are explicitly synthetic protocol test data, not claims about a real service or customer.

## Live negative calls

- Wrong definition hash: rejected at consumer/LATCH exact-binding check.
- Wrong action hash: rejected at consumer/LATCH exact-binding check.
- Initiator attempted to arm: rejected; only the bound consumer may arm.
- Early resolve: rejected because the observation window had not opened.
- Terminal resolve replay: rejected because the latch was no longer armed.
- Callback retry after acknowledgement: rejected because the consumer already acknowledged terminal state.
- Wrong callback sender and duplicate callbacks: covered by Direct Mode cases; no malicious consumer contract was deployed solely to fabricate a failed callback.

The test latch for early resolution was left armed after the negative call; the call did not alter state. This does not affect either deployed contract or any successful lifecycle.

## Fee reporting

Method-call value was 0 GEN and receipts showed `value_credited: false`. The stable RPC returned `eth_gasPrice=0x0` and a generic `eth_estimateGas=0x7a120`; neither is a reliable settled Studionet fee quote. Receipts expose `gaslimit` and leader VM `gas_used`, not settled fee/refund. No monetary fee is inferred; details are in [DEPLOYMENT.md](DEPLOYMENT.md).

## GitHub target

The repository remote is `https://github.com/Ifem1/latch.git`, branch `main`. The retry-fixture evidence update was pushed as `fcf20ee`; final documentation/evidence is committed and pushed separately. No alternate GitHub remote is used.
