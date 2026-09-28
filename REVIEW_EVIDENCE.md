# Reviewer evidence ledger

LATCH is a standalone reusable Intelligent Contract primitive, with a separate minimal cooperating consumer. It has no frontend. The protocol freezes the initiator, consumer, subject, condition, evidence URLs, source threshold, timing, and exact provisional action hash. Validators independently re-fetch public evidence. Only a finalized terminal callback changes cooperating consumer state, and acknowledgement is tracked separately.

## Reproducible local checks

| Check | Result |
|---|---|
| Stable CLI / configured chain | GenLayer CLI 0.39.1; Studionet 61999 |
| Static preflight | `python scripts/preflight.py` PASS |
| Source manifest | `python scripts/source_manifest.py` PASS |
| Direct Mode suite | 38 passed |
| GenVM lint + semantic validation, LATCH | PASS; GenVM v0.2.16, linter 0.11.0, 15 methods (8 views, 7 writes) |
| GenVM lint + semantic validation, consumer | PASS; 7 methods (3 views, 4 writes) |
| Live chain guard | RPC `https://studio.genlayer.com/api` reported exactly 61999 before deployment and live verification |

The suite covers immutable binding, consumer-only arming, observation timing, grounded evidence, independent validator checks, bounded retry and callback behavior, expiry, cancellation, unsafe inputs, callback authentication/idempotency, acknowledgement binding, and provisional-credit isolation.

## Final source deployments

| Contract | Address | Deployment transaction | Source SHA-256 |
|---|---|---|---|
| LATCH | `0xAE6E86F53fDCF676F2A0176F4E2752Bdf9725434` | `0xbd185cf38fce9e3e3b15ba9edad263e50963aa56f6a7a9dd797abe6682c3b341` | `fd38e67b638ee8d16130178efef920a91ed8ae79a359608afc7e56fcc8ad1b81` |
| ExampleLatchedGrant | `0x77D1c0C41D124b3cA9E24F6E04E2a104043a87e7` | `0x5db9a295094a516add56c8e03f99446bdf876de3b7032d32635d41d328871b0a` | `299e44ec32d6bbb154d45c516f612073aee4548e2fe0f221e57e870b270c17c0` |

Both deployment receipts were FINALIZED with MAJORITY_AGREE (5/5). `genlayer code` fetched each deployed source; each returned source contains the full corresponding local source byte-for-byte. Details and full transaction paths are in [DEPLOYMENT.md](DEPLOYMENT.md).

## Live lifecycle results

- **SATISFIED:** latch 2 committed; finalized child commit callback; consumer grant committed; usable credit increased 0→5; finalized consumer acknowledgement recorded as COMMITTED.
- **FAILED:** latch 3 became REVERT_REQUIRED; finalized revert callback; grant became REVERTED; usable credit remained 5; finalized acknowledgement recorded as REVERTED.

Both lifecycles ran against the final deployed contract pair on chain 61999. All parent and child transactions reached FINALIZED / MAJORITY_AGREE. Fixture content is synthetic, publicly readable protocol test data.

## Fee observations

Calls sent zero GEN application value. The stable RPC's zero `eth_gasPrice` and generic `eth_estimateGas` are not reliable settled fee measurements. Receipts did not provide a settled fee/refund field, so no actual transaction fee is claimed.

## GitHub target

The only configured remote is `https://github.com/Ifem1/latch.git`; the intended branch is `main`.
