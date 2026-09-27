# Deployment and live evidence

## Canonical target

- Network: **GenLayer Studionet**
- Chain ID: **61999**
- RPC: `https://studio.genlayer.com/api`
- Explorer: `https://explorer-studio.genlayer.com`
- Stable CLI: `0.39.1`
- Stable GenVM used for lint: `v0.2.16`

Before every live deployment or test phase, run `python scripts/check_network.py`. It independently queried the canonical RPC throughout this run and returned chain ID `61999`. Any other result is a hard stop.

## Finalized deployments

| Contract | Address | Deployment transaction | Final result | Source SHA-256 |
|---|---|---|---|---|
| LATCH | `0x8BC6278e19CB5c40DDcBDb7c3Dc8fCbEDdd2096C` | `0x67da2b39085c1532db75069e0e9ede473272a1b08cc59eb876189216c7e4bb5c` | FINALIZED, MAJORITY_AGREE, SUCCESS | `07f08b6b4d79835abbb0b7275d674667c52a23a8dbb2090f68d5ac60f85dce9d` |
| ExampleLatchedGrant | `0xf4eCC1CD4A811C37fA31669aFd8fA238a1fc8C93` | `0xd6f64aff7f5586d6448790f95c14a36b22a46484a2f1b29dfef68b240cfc5987` | FINALIZED, MAJORITY_AGREE, SUCCESS | `81609ff0b41c51f0da7eac4ebffa810f7a1b23d59c3f4f76e9a1d5ff65b8be27` |

The consumer was deployed with the LATCH address above. Its live `stage_grant` calls successfully queried that exact LATCH contract and finalized child `arm_latch` transactions, verifying the binding.

Deployed code was fetched from Studionet with `gen_getContractCode`, base64-decoded, and compared byte-for-byte with the repository source. Both byte lengths and SHA-256 values matched. Both deployed sources correspond to Git source commit `c7fe053735a2d78b2a446d832709d7e6abf529bd`; later commits changed fixtures and documentation only.

## Live lifecycle evidence

All listed parent and child transactions reached FINALIZED / MAJORITY_AGREE. Latch and grant state below was read back from the deployed contracts after finality.

### SATISFIED → commit → acknowledgement (latch 1)

- Create `0xf38d4a8bf3c0e8466672804a43d31085c7e1579b1bf86ef515e89cd2882d677c`
- Staging consumer grant `0x7e421db0de0d090008760faba3ca08824aa0582cae81945961022ad2f5e1d9ff`
- Finalized child arm `0x1092b6ac6186c91548af34678f39fd6eb30c108a4dd2a714642d352cf6e47586`
- Validator-backed resolve `0x6c91da3494a9baf3aa0e7e9ea962dd55f6726c4549de55d06c9b9689309dbc9b`
- Finalized `latch_commit` callback `0x9b47560175c9a28ae5eb421e00e05c0fc2e46c36d9314c15c68cfc0acd188ba5`
- Finalized acknowledgement `0x350bd656dfdc28b6b28ff174d80b84531097ecf87aa217d49006a4e75bd048a4`
- Read-back: LATCH `COMMITTED`, outcome `SATISFIED`, grounded excerpt recorded, callback count 1, acknowledgement `COMMITTED`; grant `COMMITTED`; usable credit moved from 0 to 100.

### FAILED → revert → acknowledgement (latch 2)

- Create `0x91f79c2aa30c20e95351b86ad944dc4ca61a606bbf5d3fd9a02ad5110af29628`
- Stage `0xc6c4874a3abc49c2a5428b5293e38cacbf7afef3c701382bffb10ce508a3a913`
- Finalized child arm `0x5d11167a00bcdcf6f6830454cf2d84ee790aa73f1cc4cb0b1388a07748b490c0`
- Validator-backed resolve `0x6c9b2cb7b5fcdad9ea10a52e976b6cda56393776e23dde8161c7effa2e61f507`
- Finalized `latch_revert` callback `0xab4d6f0f81264ae1d2362ef3be2ce465f58ffc7e07bf90fea88770feee1afc51`
- Finalized acknowledgement `0x458deb865399ea13d12e19e99b910d80da1a43b5aaf5d08629b23556a0a788ea`
- Read-back: LATCH `REVERT_REQUIRED`, outcome `FAILED`; grant `REVERTED`; acknowledgement `REVERTED`; usable credit remained 100.

### Insufficient availability (latch 3)

- Create `0x30fa1e92774c5cbbe6c212bd7b1457300e7bd918abe9b6023d2b8d260c77ffdc`
- Stage `0x734f07a25f45a9d9a81cc16955b9e48431bbf52c8c4c55a7d76bb766929ebb71`
- Finalized child arm `0x3f72cb84827d1d47a4f7b636bc414ada914af6bae65cb83abedf99ae39a1d234`
- Resolve `0xa1fa6b2b1d4d613d0714379fc6ef4d02ff16fda98700fd174bfc1948289c860e`
- Read-back attempt 3: outcome `UNAVAILABLE`, available mask `10`, reason “only 1 of 2 required sources were available,” terminal false. LATCH stayed `ARMED`; callback count 0; grant stayed `PROVISIONAL`; usable credit remained 100.

### INCONCLUSIVE → public evidence revision → retry (latch 4)

- Create `0xbd4e544c2cbf26a28ca99986401b0c9adb1025fbc8db32c1a931ffa1d31a8fa4`
- Stage `0x8f91bf88edef0d4129c7525a1d0d015ea65d63c21e9ff99e8dddd50903e8ca1e`
- Finalized child arm `0x299df405d6decf2a20ed731d3d25cc13e9025e93ca229d43b0ecd7333a233c63`
- First resolve `0x245afa9f02e462288418ec4d3b488767f1682173bb65c45416cc32870235e349`; read-back attempt 4 was `INCONCLUSIVE`, terminal false; LATCH remained `ARMED`, callback count 0.
- After the frozen 30-second retry cooldown, the same public fixture URL was updated in Git commit `fcf20ee` from `PENDING` to `ACTIVE`. The earlier PENDING revision remains in Git history; the fixture is explicitly synthetic.
- Retry resolve `0xb6a2ce8e38c75b092226ab5d5ee8bbd7fcea569b64c14b72b6b709dc3536f154`; read-back attempt 5 was `SATISFIED`, terminal true, with a matching verbatim excerpt.
- Finalized commit callback `0x857d3ea5e99cb9082698d16685a4afdad04d44352bf4f29f5864b637e6a57005`
- Finalized acknowledgement `0x70ef21bb407d9e652c0b55ecd532292c6135d45f84b97cccb59bb3d9e84bac8f`
- Read-back: latch `COMMITTED`; grant acknowledgement `COMMITTED`.

### Deadline expiry (latch 5)

- Create `0x94e86feb868a77691e298024f6c6fd0182a817fcd3dc7f24139c99e2a40b122f`
- Stage `0xfcf3bafabad0a52684a5b591221f1cd80cc8457271353476e3d5b9cf61ad0752`
- Finalized child arm `0xa0b477466da71be751b3d2f1c57596d48f8aa27386fbd57cd1cf64188db84d38`
- On-chain deadline: `1790544475`; expiry ran at `1790544508`.
- `expire_latch` `0x7b14625aa63481c545196a9c60bc31fcfabf019c1e410b9168af2b6b732e0214`
- Finalized revert callback `0x350595d9772ddc4c7485e5e0aad461b68438e69e3f9a487cba482d7ab6eb8236`
- Finalized acknowledgement `0x44e28d5f7fa17851e2f20d74066ad2aad3b85aa6e927096b8ff299c2900e1484`
- Read-back: LATCH `REVERT_REQUIRED` with deadline-expired reason; grant `REVERTED`; acknowledgement `REVERTED`; usable credit remained 125 (the earlier 100 + 25 committed grants only).

### Live negative paths

Each transaction finalized with the recorded leader error; no unintended state transition occurred.

| Check | Transaction | Finalized leader result |
|---|---|---|
| Wrong definition hash on consumer staging | `0x71636f8bc0ef36d5a3d4bf704f86edf05fbd464ad280c49cdd05778750dbdc01` | `EXPECTED: latch binding is not armable for this exact grant` |
| Wrong action hash from substituted grant purpose | `0x47004c4b88550c13acebbc91b9074da7b558ed8d578475d1dbb7630d68537b60` | `EXPECTED: latch binding is not armable for this exact grant` |
| Initiator tries to arm as non-consumer | `0x8b00f63b9a1a5b1fa0b5a7c4ad0695ed0453a626e1e073a76a33137c51d667e2` | `EXPECTED: only the bound consumer may arm the latch` |
| Resolve before observation window | `0x28642b2efcb63e186fb3b6b879ed4f7aadc0733e3b00572b1b713375afc0d0a0` | `EXPECTED: observation window has not opened` |
| Resolve after terminal commit | `0x2d788ba01ef43c70bfacb424429a68764ada7c305ece827540cb379ed7f06771` | `EXPECTED: latch is not armed` |
| Retry callback after acknowledgement | `0x5dfd1fbd8549c591167e1e667a5543a97d98874b8627476ec1ed445e55e7fa80` | `EXPECTED: consumer already acknowledged terminal state` |

Wrong callback sender rejection and duplicate callback idempotency are also covered in Direct Mode tests. A persistent missing-ack/failed-child scenario was not fabricated; the live network delivered the callbacks successfully. Redundant retry after acknowledgement was rejected live as shown above.

## Local validation

- `python scripts/preflight.py`: PASS.
- `python scripts/source_manifest.py`: PASS; records both source hashes above.
- `python -m pytest tests/direct -v`: **30 passed**.
- `genvm-lint check contracts/latch.py` (`GENVM_VERSION=v0.2.16`): lint and semantic validation passed, 14 methods.
- `genvm-lint check contracts/example_consumer.py` (`GENVM_VERSION=v0.2.16`): lint and semantic validation passed, 6 methods.
- Contract source sizes: LATCH 42,423 bytes; ExampleLatchedGrant 11,104 bytes.

## Transaction value and fee observations

- Application transaction value sent for the recorded method calls: **0 GEN**. Receipts show `value_credited: false`.
- The stable RPC returned `eth_gasPrice = 0x0`; its generic `eth_estimateGas` response was `0x7a120` (500,000 units) for a probe. That response is not a reliable Studionet GEN-fee quote.
- GenLayer transaction receipts expose `gaslimit` (for example, 537 on the LATCH create and 539 on resolution) and leader VM `gas_used` (reported 0 on the inspected resolve receipt), but do not expose a settled GEN fee/refund field or a reliable settled gas charge.
- Therefore actual settled transaction fees and reliable fee estimates are **not available from this stable RPC receipt interface**; none are inferred from `gaslimit`, zero `gasPrice`, or application value.

## Current source identity

The deployed source is pinned to `c7fe053735a2d78b2a446d832709d7e6abf529bd`. The repository continues on `main` at `Ifem1/latch`; the public retry fixture update commit is `fcf20ee`. See the final Git commit for this evidence ledger.
