# Submission notes

## Contribution type

**Intelligent Contracts**

## One-line description

LATCH is a semantic two-phase-commit primitive that lets cooperating Intelligent Contracts stage provisional state, then commit or unwind it only after GenLayer validators independently verify a frozen public postcondition.

## Why this is a contract primitive rather than a project

There is deliberately no frontend or product workflow. LATCH exposes a bounded protocol other builders can compose with:

```text
create definition → consumer arm → observe → commit/revert → finalized callback → acknowledgement
```

`contracts/example_consumer.py` exists only to demonstrate the integration boundary. It is not a frontend or a separate product.

## What GenLayer consensus does

GenLayer is used only where ordinary deterministic contracts cannot safely decide the result: whether public evidence establishes the exact postcondition frozen before the provisional action was armed.

Leader and validators independently fetch the source set and classify the same condition. Validators require agreement on the decision-bearing outcome, then check that the leader's verbatim excerpt and source index are supported by their own fetch and materially align with their independently selected support excerpt. The stored availability mask is leader-observation metadata; exact per-source bitmap agreement is not claimed.

## What deterministic code does

All protocol mechanics are deterministic:

- definition/action hashing;
- consumer binding;
- arming;
- observation-window timing;
- minimum-source availability;
- retry cooldown;
- attempt bounds;
- state transitions;
- timeout-to-revert;
- callback retry limits;
- consumer acknowledgement;
- exact compact integration checks.

The model cannot choose callback recipients, action hashes, deadlines, source thresholds or timeout policy.

## Key distinction

LATCH does not ask an LLM to decide whether an action should happen.

The action already exists provisionally and is cryptographically bound. GenLayer only decides whether the frozen real-world postcondition has caught up with that provisional transition.

## Safety invariant

Unresolved expiry can never commit state. The only automatic timeout path is:

```text
ARMED → REVERT_REQUIRED
```

## Intended reusable cases

- service credits that become usable only after public activation;
- provisional entitlements pending external fulfilment;
- staged marketplace state pending public delivery evidence;
- configuration changes that remain provisional until a public health postcondition is established;
- autonomous workflows that need a semantic commit/rollback boundary.

## Network

Final target is stable GenLayer Studionet, chain ID **61999**.

## Evidence status

Source, threat model, Direct Mode suite, stable-network guard, and live-run evidence are included. LATCH and ExampleLatchedGrant are deployed and finalized on Studionet 61999; deployed code fetched from the RPC matches the repository byte-for-byte. Live SATISFIED/commit and FAILED/revert lifecycles both finalized through consumer acknowledgement. Bounded retry, source availability, expiry and negative arming paths are covered in Direct Mode; the evidence ledger distinguishes these from live demonstrations.

The public lifecycle fixtures are explicitly synthetic test evidence. They demonstrate the protocol and do not claim any real-world customer or service event. Transaction fees are not reported as settled because the stable RPC receipts do not expose a reliable settled fee/refund amount.
