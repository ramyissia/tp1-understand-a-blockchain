# TP1 - Understand a blockchain by building one: written answers

EFREI / Digital Finance, session 1. Every number below comes from the run saved in
[console_log.txt](console_log.txt) (`python blockchain.py`). Timings depend on the machine.

## Mission and security question: prediction

**Prediction (before coding):** if a stored transaction changes, the block's stored hash no
longer matches a fresh calculation from its data, so validation fails at that block. If the
attacker also recalculates that block's hash, the next block still stores the old hash in its
`previous_hash`, so the link breaks. With Proof-of-Work, a recalculated hash will almost never
start with the required zeros. The chain does not stop the change, but it makes the change
detectable.

**Result:** confirmed by Exercise 3 (Part C and step 16) and by the Exercise 4 extension.

## Exercise 1: what changes when data changes?

| Input | SHA-256 |
|---|---|
| `Alice pays Bob 10 tokens` | `87a8855cfad9014bf689545effe49a836d2a987ad9a61b7e2cee77dc98f92528` |
| `Alice pays Bob 100 tokens` | `4d4c26069369ff513a541920af0d84ff9ced700351788f2cd3112ebe7b8b78ec` |

**Observation:** adding a single `0` changed 62 of the 64 hex characters (142 of the 256 bits).
The two digests look unrelated, and the second one gives no clue about what was edited
(avalanche effect). Running the original text twice gives exactly the same digest.

Changing only capitalization or spacing also produces a completely different digest
(between 120 and 139 bits changed): `alice...`, `ALICE PAYS BOB...`, a trailing space and a
double space all fail to match. SHA-256 hashes bytes, and `a` / `A` or an extra space are
different bytes.

**Q1. Does hashing encrypt the transaction?**
No: encryption is reversible by whoever holds the key, while hashing is a one-way fingerprint
with no key, which anyone can compute but nobody can turn back into the text.

**Q2. What must remain identical to get the same digest?**
The exact same bytes: same characters, same case, same spaces and punctuation, same encoding
(UTF-8), and the same algorithm (SHA-256).

**Q3. Can you reconstruct a transaction from its digest alone?**
No. SHA-256 is one-way: the only method is to guess inputs and compare their digests.
Caveat: if the possible inputs are few and predictable (for example
`Alice pays Bob N tokens` for N up to one million), guessing them all is fast. A hash proves
integrity; it does not hide low-variety data.

## Exercise 2: design a block (Checkpoint A)

Rule used in `Block.calculate_hash()`:

```
index|timestamp|data|previous_hash|nonce   ->  UTF-8 bytes  ->  SHA-256 hex digest
```

Test A output:

```
string hashed for b1: 1|0|Alice -> Bob: 10|abc|0
b1 hash: 03f7f88d2d984e0c0fe628580224330acc68a72489d98b0d5a544f50760dd8d8
b2 hash: 03f7f88d2d984e0c0fe628580224330acc68a72489d98b0d5a544f50760dd8d8
same fields: True
changed data: True
```

- **Fixed order and separator:** without a separator, index `1` + timestamp `23` and
  index `12` + timestamp `3` would both give `123` and the same hash.
- **`hash` is excluded:** a block cannot contain its own digest, because the digest would
  change as soon as it is written.
- **`nonce` is included:** otherwise mining could never change the hash.
- **Fixed timestamp in tests:** `time.time()` changes every call, so two blocks are identical
  only when the timestamp is fixed.

## Exercise 3: chain and tampering (Checkpoint B)

```
#0  prev=0             hash=bb80aa320d18  data='Genesis'
#1  prev=bb80aa320d18  hash=46537ae02d5d  data='Alice -> Bob: 10'
#2  prev=46537ae02d5d  hash=b302f0bef246  data='Bob -> Cara: 3'

before: True
after:  False
  reason: block 1: stored hash does not match a fresh calculation (its data changed)

after recalculating block 1: False
  reason: block 2: previous_hash does not match the hash of block 1 (broken link)
```

- **Step 15:** `is_valid()` recalculates block 1's hash from its current data
  (`Alice -> Bob: 100`). The result differs from the stored hash, which was calculated
  from `Alice -> Bob: 10`.
- **Step 16:** after recalculating block 1's hash, block 1 is consistent with itself, but
  block 2 still stores the old hash `46537ae02d5d...` in `previous_hash`. The link is broken,
  so validation still fails.
- The validator only reads. It never writes `block.hash`, so calling it cannot repair a
  tampered chain.

**Q4. Why does changing an earlier block affect the links of later blocks?**
Each block stores the previous block's hash, and that `previous_hash` is itself part of the
data that gets hashed. Changing block 1 changes its hash, so block 2 now points to a hash that
no longer exists. Fixing block 2's `previous_hash` changes block 2's hash, which breaks block 3,
and so on. One edit forces the attacker to rebuild every later block.

**Q5. If one person controls a single local chain and recomputes every hash, is the data
trustworthy?**
No. Validation only proves that the chain is consistent with itself, not that its content is
true. The extension demo shows it: after re-mining block 1 and block 2, the forged chain
passes `is_valid()` (it took a few milliseconds at difficulty 3). Real blockchains add:

- **many independent copies** (peer-to-peer nodes), so one rewritten copy is outvoted;
- **a consensus rule** (most cumulative work for PoW, staked votes for PoS), so rewriting
  history means out-computing or out-staking the honest majority;
- **digital signatures**, so only the holder of Alice's private key can spend Alice's tokens;
- **transaction rules** checked by every node (sufficient balance, no double spending);
- **economic incentives** (block rewards, fees, penalties) that make honesty pay.

## Exercise 4: Proof-of-Work

Observation table (Test C, block `Alice -> Bob: 10`, `previous_hash="abc"`, `timestamp=0`):

| Difficulty | Nonce found | Elapsed time (s) | Hash prefix |
|---|---|---|---|
| 2 | 64 | 0.0001 | `000ef7a072ff` |
| 3 | 64 | 0.0001 | `000ef7a072ff` |
| 4 | 11796 | 0.0143 | `0000a0d5ae4c` |

Difficulties 2 and 3 give the same nonce: the search always starts at nonce 0 on the same
block, and the first hash starting with `00` (nonce 64) also happens to start with `000`.
That run was lucky: about 4,096 attempts are expected at difficulty 3.

Repeated runs, 5 different blocks per difficulty (step 20):

| Difficulty | Expected attempts (16^d) | Nonces found | Times (s) |
|---|---|---|---|
| 2 | 256 | 457, 9, 120, 52, 318 | 0.0007, 0.0000, 0.0001, 0.0001, 0.0004 |
| 3 | 4,096 | 5154, 7183, 8713, 10934, 1008 | 0.0062, 0.0092, 0.0108, 0.0134, 0.0012 |
| 4 | 65,536 | 168174, 95316, 65943, 41710, 52174 | 0.2031, 0.1201, 0.0820, 0.0503, 0.0636 |

Extension (step 21): with `Blockchain(difficulty=3)`, `add_block()` mines new blocks and
`is_valid()` checks the zero prefix for every block after genesis (genesis is not mined, so it
is checked against its original contents instead). Recalculating a tampered block's hash
without mining now fails the PoW rule:
`block 1: hash does not start with 3 zero(s) (PoW rule)`.

**Q6. Why does a higher difficulty usually need more attempts? Why can one run be faster?**
Each hex character of a hash behaves like a random draw among 16 values, so the chance that a
hash starts with *d* zeros is (1/16)^d. That means about 16^d attempts on average: 256, then
4,096, then 65,536. Each extra zero multiplies the work by 16. Each nonce is an independent
lottery ticket, so a run can win early or late: at difficulty 4 the nonces found ranged from
41,710 to 168,174, and at difficulty 3 Test C won at nonce 64. Timings also move with what
else the computer is doing. Checking a solution, by contrast, costs a single hash.

**Q7. One practical limitation of PoW, and how is Proof-of-Stake different?**
PoW security comes from spending electricity and specialised hardware: it is energy-hungry,
and mining concentrates where power is cheap. In Proof-of-Stake, validators lock up coins as
collateral and are selected to propose and confirm blocks in proportion to that stake;
cheating is punished by destroying part of the stake (slashing). Security comes from capital
at risk rather than from computation, which uses far less energy.

## Debugging challenge: one validation error

**Error:** a validator that only checks the links (`buggy_is_valid` in `blockchain.py`):

```python
for i in range(1, len(chain.blocks)):
    if chain.blocks[i].previous_hash != chain.blocks[i - 1].hash:
        return False
return True
```

**Justification:** it compares two stored values and never recalculates a hash from the data.
After changing block 1's data to `Alice -> Bob: 100` without touching any hash, every stored
link still matches, so it returns `True` and accepts the forgery. The correct `is_valid()`
returns `False` with `block 1: stored hash does not match a fresh calculation`.
**Fix:** also require `block.hash == block.calculate_hash()` for every block (and the PoW prefix
once mining is added).

This test is meaningful because it fails for the right reason: the edit is a data change only,
so the only way to catch it is to recompute the hash from the data.

Another classic error to avoid: a validator that "repairs" the block before checking
(`block.hash = block.calculate_hash()`), which erases the evidence and always returns `True`.

## Project bridge: dApp proposal

**dApp: crowdfunding escrow for a student association project.**

| | |
|---|---|
| **Data** | Campaign goal, deadline and beneficiary address; each contributor's address and amount; total raised. The project description stays off-chain, with only its hash stored on-chain to prove it was not modified afterwards. |
| **Action** | `contribute()` before the deadline; after the deadline, `claim()` by the beneficiary or `refund()` by a contributor. |
| **On-chain rule** | If the total raised reaches the goal by the deadline, only the beneficiary can withdraw the funds, once. Otherwise each contributor can withdraw exactly what they put in. Nobody, not even the organiser, can move the funds any other way. |

This rule belongs in a smart contract because it is objective, can be checked from on-chain
data alone, and guards money held for people who do not fully trust each other.

## What this classroom simulation does not prove

It is a Python list on one computer. It shows data integrity (any edit is detectable) and the
cost asymmetry of Proof-of-Work. It does not show:

- **networking:** there is no peer-to-peer propagation of blocks or transactions;
- **transaction signatures:** anyone can write `Alice -> Bob: 10`;
- **distributed agreement:** there are no competing chains and no fork-choice rule;
- **adversarial security:** the person who owns the list can rewrite it entirely, as Q5 shows;
- **business rules:** balances and double spending are not checked.
