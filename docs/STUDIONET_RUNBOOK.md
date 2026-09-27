# Studionet 61999 runbook

This runbook is deliberately specific. Do not substitute the preview network.

## 1. Environment guard

```bash
python scripts/check_network.py
```

Expected:

```text
chain id: 61999
OK: stable GenLayer Studionet / chain 61999
```

## 2. Tooling

Use the stable Studionet release family. At the time this repository was prepared, the canonical CLI reference reports `0.39.1`.

```bash
genlayer --version
genlayer network set studionet
```

Do not switch this repository to the Studio development preview.

## 3. Local checks

```bash
pip install -r requirements-test.txt
python scripts/preflight.py
python -m pytest tests/direct -v
GENVM_VERSION=v0.2.16 genvm-lint check contracts/latch.py
GENVM_VERSION=v0.2.16 genvm-lint check contracts/example_consumer.py
python scripts/source_manifest.py
```

## 4. Deploy LATCH

```bash
genlayer deploy --contract contracts/latch.py --rpc https://studio.genlayer.com/api
```

Wait for finality and record both transaction and address.

## 5. Deploy example consumer

Deploy `contracts/example_consumer.py` with the finalized LATCH address as its constructor argument.

## 6. Prepare exact action hash

Use the consumer's read-only `preview_grant_action_hash` with:

- beneficiary;
- amount;
- purpose.

Record the resulting hash.

## 7. Create latch

Use that action hash and the consumer address. Freeze a short reviewer-friendly criterion with one or two public HTTPS fixture pages that clearly state a status.

Recommended live demo values:

```text
observation_delay_seconds = 60
resolution_window_seconds = 600
retry_cooldown_seconds = 60
```

Do not use ephemeral pages likely to change during the review.

## 8. Stage provisional consumer state

Call `stage_grant(...)` on the consumer. Verify:

```text
grant state = PROVISIONAL
usable credit = 0
```

Wait for the finalized child `arm_latch` transaction and verify the latch is `ARMED`.

## 9. Commit path

After `observe_after`, call `resolve_latch` against evidence that clearly meets the postcondition.

Verify in order:

```text
LATCH = COMMITTED
callback scheduled
consumer grant = COMMITTED
usable credit increased
consumer acknowledgement = COMMITTED
```

Record every finalized parent/child transaction.

## 10. Revert path

Create a separate latch against a fixture that clearly states failure. Repeat staging/arming and prove:

```text
LATCH = REVERT_REQUIRED
consumer grant = REVERTED
usable credit unchanged
acknowledgement = REVERTED
```

## 11. Inconclusive/retry path

Use evidence that initially states only a pending status. Verify first observation remains `ARMED`. Update/use a second controlled public fixture only if the evidence provenance is honest and recorded, then retry after cooldown and prove terminal resolution.

## 12. Expiry path

Create an armed latch that never obtains a determinate postcondition. After the exact deadline call `expire_latch` and verify fail-closed reversion.

## 13. Final source verification

Fetch deployed contract code and compare it to the exact repository source. Update `DEPLOYMENT.md` and `REVIEW_EVIDENCE.md` with the resulting hashes and explorer links.
