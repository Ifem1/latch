# LATCH security model

## Trust boundary

LATCH does not trust:

- the latch initiator to describe later evidence honestly;
- the consumer to arm any definition other than the one it explicitly accepts;
- the consensus leader's semantic result;
- source-page instructions;
- one source being available when the definition requires several;
- callback delivery to succeed on the first child transaction;
- a human-readable action description to identify the action.

It does trust GenLayer consensus/finality and the cooperating consumer contract's own implementation once that consumer opts in.

## Threats and mitigations

### Definition substitution

**Threat:** change the success condition, evidence sources, timing or consumer after provisional state exists.

**Mitigation:** all material latch fields are included in `definition_hash`. The consumer arms only while pinning that exact hash.

### Action substitution

**Threat:** use a successful observation for action A to commit action B.

**Mitigation:** the exact provisional action is represented by `action_hash`; arming, compact views and terminal callbacks all carry that hash.

### Fake consumer binding

**Threat:** create a latch naming an arbitrary contract and claim it participates.

**Mitigation:** a latch remains inert in `CREATED` until the bound consumer itself calls `arm_latch`.

### Prompt injection in definition text

**Threat:** make user-controlled definition text instruct validators to ignore the protocol task.

**Mitigation:** common control-instruction markers are rejected, all definition/source fields are rendered as untrusted JSON data, and prompts explicitly forbid following embedded instructions.

### Prompt injection in source pages

**Threat:** a webpage tells the validator to change outcome, call tools or reveal hidden instructions.

**Mitigation:** source material is framed as untrusted evidence; the task and allowed labels are fixed outside source content. Determinate results must also ground a verbatim excerpt in independently rendered evidence.

### Leader-only judgement

**Threat:** malicious leader returns a plausible-shaped but false result.

**Mitigation:** `run_nondet_unsafe` validators independently fetch the frozen evidence and re-run the classification. Decision-bearing outcomes must match.

### Evidence withholding / cherry-picking

**Threat:** settle from one convenient source when the definition required a broader evidence surface.

**Mitigation:** `min_sources` is evaluated programmatically before LLM judgement. Insufficient availability returns `UNAVAILABLE`, not success/failure.

### Fabricated evidence quote

**Threat:** leader gives the correct label with invented supporting evidence.

**Mitigation:** for determinate outcomes, the leader excerpt must be verbatim in the validator's independently fetched source at the stated index. The validator then independently checks whether that exact excerpt materially supports its own decision-bearing outcome.

### Timeout-to-success

**Threat:** allow successful commitment merely because no one could prove failure.

**Mitigation:** expiry always transitions to `REVERT_REQUIRED`.

### Repeated observation spam

**Threat:** participant fills storage or repeatedly invokes costly consensus.

**Mitigation:** participant-only resolution, retry cooldown and `MAX_ATTEMPTS`.

### Callback replay

**Threat:** the same terminal callback is delivered multiple times.

**Mitigation:** callback consumer must be idempotent. The included example implements idempotent terminal handlers and re-emits acknowledgement when safely repeated.

### Accepted-state irreversibility

**Threat:** emit a consumer callback before GenLayer appeal finality.

**Mitigation:** all consumer callbacks and acknowledgements use `on="finalized"`.

### Failed child callback

**Threat:** LATCH reaches a terminal state but the consumer child transaction fails.

**Mitigation:** LATCH records callback attempts separately from consumer acknowledgement. Participants may call `retry_callback` within bounded retry/cooldown rules until the consumer acknowledges.

### Arbitrary real-world rollback claim

**Threat:** imply that a failed latch can undo an external action such as an API call, shipment or irreversible payment.

**Mitigation:** LATCH makes no such claim. `REVERT_REQUIRED` is a protocol signal to cooperating contracts. Only state explicitly designed to be provisional can be unwound.

## Residual risks

- Public sources can be wrong or coordinated; LATCH proves validator consensus over the frozen evidence surface, not metaphysical truth.
- Dynamic webpages can change between nodes; disagreement should prevent consensus rather than silently force a result.
- `min_sources` proves availability count, not independence of ownership/control.
- A badly designed consumer can still expose provisional state as spendable before commit. LATCH cannot repair a consumer that violates its integration contract.
- A terminal child callback can fail repeatedly because of consumer bugs. The LATCH state remains terminal and auditable; delivery is not falsely reported as acknowledged.
