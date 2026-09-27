# Architecture

## Protocol boundary

LATCH is not a generic escrow, oracle or workflow engine. It owns one boundary:

> convert a cooperating consumer's exact provisional state transition into a final commit/revert instruction after consensus-backed observation of a pre-frozen public postcondition.

## Actors

### Initiator

Creates the latch definition. Cannot arm a latch on behalf of the consumer.

### Consumer contract

Owns provisional state. It must explicitly arm the exact definition/action and implement idempotent `latch_commit` / `latch_revert` handlers.

### GenLayer validators

Independently inspect the frozen evidence set and classify the frozen postcondition.

### Keeper/participant

Only initiator or consumer may trigger semantic observation attempts. Expiry itself is permissionless once the deadline passes.

## Two-phase model

### Phase 1: prepare

```text
create_latch
    ↓
consumer verifies definition + action hash
    ↓
consumer stages provisional local state
    ↓
consumer emits arm_latch
```

The consumer is responsible for ensuring provisional state is non-final and non-spendable.

### Phase 2: semantic commit

```text
resolve_latch
    ↓
independent evidence observation
    ↓
SATISFIED / FAILED / INCONCLUSIVE / UNAVAILABLE
```

Only `SATISFIED` commits. Only `FAILED` or deadline expiry require revert. The other outcomes remain armed.

## Delivery vs decision

LATCH deliberately stores two separate notions:

1. **semantic terminal state**: `COMMITTED` or `REVERT_REQUIRED`;
2. **consumer acknowledgement**: whether the final instruction was applied.

An asynchronous child transaction can fail even when the parent LATCH transaction is final. Keeping these states separate avoids falsely claiming successful application.

## Why callbacks use finality

A callback sent on `accepted` could execute before an appeal changes the parent result. LATCH therefore schedules consumer messages only at `finalized`.

## Definition hash

Canonical payload includes:

```text
initiator
consumer
title
subject
success condition
action hash
ordered evidence URLs
minimum available sources
observation delay
resolution window
retry cooldown
```

The consumer pins the hash when arming.

## Evidence semantics

LATCH does not claim that one public page is true. It claims that GenLayer consensus reached a bounded outcome over a frozen evidence surface and criterion.

Where stronger provenance or source-authority guarantees are required, a consumer can compose LATCH with another source-authority primitive rather than bloating this contract's scope.
