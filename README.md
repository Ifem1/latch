# LATCH

**Semantic two-phase commit for GenLayer Intelligent Contracts.**

LATCH lets a cooperating Intelligent Contract create **provisional state now**, then commit or unwind that state only after GenLayer validators independently verify a frozen real-world postcondition.

It is intentionally a **standalone contract primitive with no frontend**.

Target repository: `Ifem1/latch`
Target network: **GenLayer Studionet, chain ID 61999**
RPC: `https://studio.genlayer.com/api`

> LATCH does not claim to reverse arbitrary internet side effects. It can only commit or unwind state in contracts that deliberately integrate the protocol.

## Why LATCH exists

Ordinary smart contracts are good at deterministic preconditions:

```text
if balance >= amount:
    transfer()
```

They are much weaker when a state transition should depend on a fact that is only knowable **after** an external action has been attempted:

```text
stage credit
    ↓
external provider attempts activation
    ↓
public evidence later says whether activation succeeded
    ↓
commit credit OR unwind provisional credit
```

A naive implementation usually chooses one of two bad options:

1. **Commit immediately** and try to repair state later if the real-world action failed.
2. **Trust one server/oracle** to tell the contract whether the postcondition occurred.

LATCH provides a reusable middle layer:

```text
consumer creates provisional state
              ↓
       LATCH is armed
              ↓
    observation window opens
              ↓
GenLayer validators independently inspect
 the frozen public evidence and criterion
              ↓
      ┌───────┴────────┐
      ↓                ↓
 SATISFIED           FAILED
      ↓                ↓
 COMMITTED        REVERT_REQUIRED
      ↓                ↓
finalized IC-to-IC callback to consumer
```

If evidence remains unavailable or inconclusive until the deadline, LATCH **fails closed to `REVERT_REQUIRED`**.

## Core invariant

LATCH never decides what provisional action should exist.

The consumer first defines an exact provisional action and commits its hash:

```text
action_hash = keccak256(canonical_action_payload)
```

The latch definition freezes:

- initiator;
- consumer contract;
- action hash;
- subject;
- semantic success condition;
- public evidence URLs;
- minimum evidence-source availability;
- observation delay;
- resolution deadline;
- retry cooldown.

The consumer may arm the latch only if the expected `definition_hash` and `action_hash` both match.

Validators therefore cannot rewrite the action. They only answer the narrow postcondition question.

## State machine

```text
CREATED
  │
  │ consumer arms exact definition/action
  ▼
ARMED
  │
  ├── SATISFIED ───────────────► COMMITTED
  │                                 │
  │                                 └── finalized callback: latch_commit(...)
  │
  ├── FAILED ──────────────────► REVERT_REQUIRED
  │                                 │
  │                                 └── finalized callback: latch_revert(...)
  │
  ├── INCONCLUSIVE ─────────────► ARMED (retry later)
  │
  ├── UNAVAILABLE ──────────────► ARMED (retry later)
  │
  └── deadline expires ─────────► REVERT_REQUIRED

CREATED ── initiator cancel before arming ──► CANCELLED
```

There is **no timeout-to-commit path**.

## Consensus design

For each observation attempt, the leader and validators independently:

1. render the same frozen HTTPS source set;
2. enforce `min_sources` availability before semantic judgement;
3. evaluate only the frozen `subject` and `success_condition`;
4. classify `SATISFIED`, `FAILED`, or `INCONCLUSIVE`;
5. for determinate results, return one short verbatim evidence excerpt and source index.

The custom validator then independently re-runs the observation and requires:

- the same decision-bearing outcome;
- a valid source index;
- the leader's evidence excerpt to be present in that validator's independently rendered source;
- empty evidence for `INCONCLUSIVE` / `UNAVAILABLE`.

The leader cannot settle the latch merely by returning valid JSON.

## Evidence-availability rule

A latch can freeze up to four public HTTPS sources and a minimum-source threshold.

Example:

```text
sources = 3
min_sources = 2
```

If only one source is readable, the attempt returns:

```text
UNAVAILABLE
```

and the latch remains `ARMED`.

This prevents the leader from silently settling from an incomplete evidence surface when the definition required broader availability.

## Finalized callbacks

Terminal resolution schedules an asynchronous callback with `on="finalized"`:

```text
COMMITTED
→ consumer.latch_commit(latch_id, definition_hash, action_hash)

REVERT_REQUIRED
→ consumer.latch_revert(latch_id, definition_hash, action_hash)
```

The callback is not emitted on `accepted`, because an accepted GenLayer transaction is still appealable.

The consumer is expected to be idempotent. LATCH supports bounded callback retries and a return acknowledgement:

```text
consumer applies final state
        ↓
consumer → acknowledge_terminal(...)
        ↓
LATCH records COMMITTED / REVERTED acknowledgement
```

## Example consumer

`contracts/example_consumer.py` is deliberately small. It proves the primitive's intended boundary without turning LATCH into a product.

The example stages a provisional service credit:

```text
PROVISIONAL grant = 100
usable credit      = 0
```

Only after `latch_commit(...)`:

```text
PROVISIONAL → COMMITTED
usable credit 0 → 100
```

On `latch_revert(...)`:

```text
PROVISIONAL → REVERTED
usable credit remains 0
```

The exact grant payload is hashed before latch creation, so a callback for one action cannot finalize a different action.

## Public API

### `create_latch(...)`

Creates an immutable latch definition in `CREATED` state.

### `arm_latch(...)`

Callable only by the bound consumer contract. Starts the observation clock after exact definition/action pinning.

### `resolve_latch(...)`

Runs the consensus-backed postcondition observation. Only the initiator or consumer may spend an observation attempt.

### `expire_latch(...)`

Permissionless after the deadline. Fails closed to `REVERT_REQUIRED` and schedules the revert callback.

### `retry_callback(...)`

Allows a participant to resend a terminal callback if the consumer has not acknowledged it. Retry count and cooldown are bounded.

### `acknowledge_terminal(...)`

Callable only by the bound consumer. Records that the final callback was actually applied.

### Consumer views

- `is_armable(...)`
- `is_committed(...)`
- `is_revert_required(...)`
- `get_latch(...)`
- `get_attempt(...)`
- `get_status_dictionary()`

Every compact status view pins both `definition_hash` and `action_hash` where it matters.

## Safety properties

LATCH is designed around these invariants:

1. **No unilateral arming**: creating a latch against a contract does nothing until that exact consumer arms it.
2. **No action substitution**: `action_hash` is frozen before observation.
3. **No rule substitution**: the entire latch definition is hashed before arming.
4. **No leader-only settlement**: validators independently re-observe and re-classify.
5. **Grounded determinate outcomes**: `SATISFIED` / `FAILED` require a verbatim source excerpt.
6. **No missing-source cherry-pick**: `min_sources` is enforced programmatically.
7. **No timeout-to-success**: unresolved expiry always requires revert.
8. **No pre-finality callback**: consumer messages use `on="finalized"`.
9. **Idempotent delivery model**: consumers must accept safe callback retries.
10. **Bounded storage/liveness costs**: source count, attempts, callback retries, text sizes and retry cadence are bounded.

See [SECURITY.md](SECURITY.md) for the complete threat model.

## Repository layout

```text
contracts/
  latch.py                 main reusable primitive
  example_consumer.py      minimal cooperating consumer

tests/direct/
  test_latch.py            30 Direct Mode scenarios

tests/integration/
  README.md                required live lifecycle checks

scripts/
  check_network.py         hard chain guard for 61999
  preflight.py             static repository checks
  source_manifest.py       source hashes for review/deploy pinning

docs/
  ARCHITECTURE.md
  REVIEW_CHECKLIST.md
  STUDIONET_RUNBOOK.md
```

## Local validation

Use stable Studionet-compatible tooling:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements-test.txt

python scripts/preflight.py
python -m pytest tests/direct -v
GENVM_VERSION=v0.2.16 genvm-lint check contracts/latch.py
GENVM_VERSION=v0.2.16 genvm-lint check contracts/example_consumer.py
```

The stable hosted target is:

```text
Network: GenLayer Studionet
Chain ID: 61999
RPC: https://studio.genlayer.com/api
Explorer: https://explorer-studio.genlayer.com
```

Before any live deployment:

```bash
python scripts/check_network.py
```

That script aborts unless the RPC reports chain ID `61999`.

## Validation and live deployment status

LATCH and ExampleLatchedGrant are deployed and finalized on stable Studionet 61999. Both deployed source files were fetched from the RPC and matched byte-for-byte with the repository sources. Live validator-backed commit, failure/revert, inconclusive then retry, unavailable-source, expiry, callback and acknowledgement paths were exercised. The public lifecycle fixtures are explicitly disclosed synthetic evidence.

Local verification: `scripts/preflight.py` and `scripts/source_manifest.py` pass; Direct Mode reports 30 passing scenarios; GenVM `v0.2.16` lint and semantic validation pass for both contracts. The stable CLI is `0.39.1`.

See [DEPLOYMENT.md](DEPLOYMENT.md) for addresses, finalized transaction hashes, source hashes, lifecycle read-backs, network confirmation, fee observations and the source commit. Re-run `python scripts/check_network.py` before every live deployment or test phase; it refuses to proceed unless the canonical RPC reports chain ID `61999`.

## Submission category

This is intended for **Intelligent Contracts**, not Projects:

- no frontend;
- no product UI;
- reusable contract primitive;
- custom GenLayer consensus logic;
- deterministic state machine;
- bounded, documented integration surface;
- example consumer solely to prove composability.
