# Integration evidence

The live integration suite is not faked in CI; it requires a funded/configured Studionet account and real consensus finality. The requested live lifecycle was exercised on stable Studionet 61999. This directory intentionally does not contain synthetic transaction hashes or a second deployment harness.

The finalized transaction ledger, state read-backs and source hashes are in [DEPLOYMENT.md](../../DEPLOYMENT.md). The run covered:

- deployed LATCH and ExampleLatchedGrant contracts with byte-matched fetched source;
- exact definition/action binding, consumer-stage and finalized arm;
- provisional credit held at zero until commit;
- validator-backed SATISFIED and FAILED decisions with finalized callbacks and consumer acknowledgements;
- INCONCLUSIVE followed by retry after a public fixture commit and cooldown;
- UNAVAILABLE with one of two required sources missing;
- deadline expiry with finalized revert and acknowledgement;
- wrong hashes, unauthorized arm, early resolution, terminal replay and acknowledged-callback retry rejection.

Public fixture pages are explicitly disclosed synthetic test evidence. They do not assert a real customer/service event. Direct Mode has 30 passing scenarios; live child-message delivery was separately verified from finalized transactions.
