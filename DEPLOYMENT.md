# Deployment

## Canonical target

- Network: **GenLayer Studionet**
- Chain ID: **61999**
- RPC: `https://studio.genlayer.com/api`
- Explorer: `https://explorer-studio.genlayer.com`
- Stable CLI reference line: `0.39.1`

Run first:

```bash
python scripts/check_network.py
```

## Deployment status

**Studionet 61999 verified; live deployment not yet executed.**

`python scripts/check_network.py` now independently reports chain ID `61999` from the canonical RPC. The guard identifies its requests as `LATCH-network-check/1.0`, which avoids the endpoint's Cloudflare 1010 response to Python's default user agent. Rerun this guard immediately before every deployment and live-testing phase. Address and transaction fields remain pending until finalized network results are read back.

### LATCH

- Contract address: `PENDING`
- Deployment tx: `PENDING`
- Finalized result: `PENDING`
- Deployed source SHA-256: `PENDING`
- Source commit: `PENDING`

### ExampleLatchedGrant

- Constructor arg: deployed LATCH address
- Contract address: `PENDING`
- Deployment tx: `PENDING`
- Finalized result: `PENDING`
- Deployed source SHA-256: `PENDING`

## Required live lifecycle evidence

The final deployment is not review-ready until all of these are exercised and read back:

1. create latch with exact definition/action hash;
2. consumer stages provisional grant and arms latch;
3. prove provisional amount is unusable before commit;
4. `SATISFIED` observation → LATCH `COMMITTED`;
5. finalized callback → grant `COMMITTED` → usable amount increases;
6. acknowledgement returns to LATCH;
7. separate `FAILED` observation → `REVERT_REQUIRED` → consumer reverts;
8. `INCONCLUSIVE` attempt remains `ARMED`, then a later retry resolves;
9. source-threshold failure returns `UNAVAILABLE` and does not settle;
10. unresolved deadline expires to `REVERT_REQUIRED`;
11. wrong definition hash and wrong action hash are rejected;
12. callback retry is idempotent;
13. source code fetched from deployed contract matches the pinned repository source.

Do not claim a live validator-backed lifecycle until the relevant transactions reach finality.

## Local validation completed

- `python scripts/preflight.py`: PASS.
- `python -m pytest tests/direct -v`: 26 passed.
- `genvm-lint check contracts/latch.py` with `GENVM_VERSION=v0.2.16`: lint and validation passed (14 methods).
- `genvm-lint check contracts/example_consumer.py` with `GENVM_VERSION=v0.2.16`: lint and validation passed (6 methods).
- Stable CLI reports `0.39.1`; the repository targets the stable `studionet` alias only.
- Contract source sizes: LATCH 42,423 bytes; ExampleLatchedGrant 11,104 bytes.

Local validation is not a substitute for live consensus evidence. No live deployment or lifecycle transaction has been sent yet.
