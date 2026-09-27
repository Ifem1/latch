# Integration tests

The live integration suite is intentionally not faked in CI. It requires a funded/configured Studionet account and real consensus finality.

The final connected agent must execute the lifecycle in `docs/STUDIONET_RUNBOOK.md` and then add an automated or scripted integration harness that records:

- deployed LATCH address;
- deployed ExampleLatchedGrant address;
- finalized create/stage/arm transactions;
- finalized semantic commit transaction;
- finalized consumer callback and acknowledgement;
- finalized semantic failure transaction;
- inconclusive + later retry;
- expiry fail-closed path;
- negative hash/sender tests against the live deployment.

No mocked transaction hashes belong in this directory.
