"""
TP1 - Understand a blockchain by building one
EFREI / Digital Finance - Session 1

One file, standard library only: runs as-is in the Programiz online editor
or locally with `python blockchain.py`.

Teaching model only. A Python list of hash-linked blocks shows data
integrity and the Proof-of-Work idea. It does NOT model networking,
transaction signatures, distributed agreement or adversarial security.
"""

import copy
import hashlib
import time


def sha256(text):
    """SHA-256 hex digest of a text (Exercise 1 recipe)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ===========================================================================
# Block - Exercise 2 (calculate_hash) and Exercise 4 (mine)
# ===========================================================================

class Block:
    def __init__(self, index, data, previous_hash, timestamp=None):
        self.index = index
        self.timestamp = time.time() if timestamp is None else timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = None

    def calculate_hash(self):
        # TODO 1: one deterministic string, always the same field order and
        # the same "|" separator. self.hash is NOT part of it: a block
        # cannot contain its own digest.
        block_string = (f"{self.index}|{self.timestamp}|{self.data}|"
                        f"{self.previous_hash}|{self.nonce}")
        # TODO 2: string -> UTF-8 bytes -> SHA-256 hexadecimal digest.
        return sha256(block_string)

    def mine(self, difficulty):
        # TODO 5: try nonce = 0, 1, 2, ... until the digest starts with
        # `difficulty` "0" characters. With difficulty 0 the first hash is
        # accepted, so mine(0) simply calculates and stores the hash.
        target = "0" * difficulty
        self.nonce = 0
        self.hash = self.calculate_hash()
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()
        return self.hash


# ===========================================================================
# Blockchain - Exercise 3 (add_block, is_valid) + Exercise 4 extension
# ===========================================================================

class Blockchain:
    def __init__(self, difficulty=0):
        # difficulty 0  -> Exercise 3 behaviour (no mining).
        # difficulty > 0 -> Exercise 4 extension: add_block() mines new
        #                   blocks and is_valid() checks the zero prefix.
        self.difficulty = difficulty
        genesis = Block(0, "Genesis", "0", timestamp=0)
        genesis.hash = genesis.calculate_hash()
        self.blocks = [genesis]

    def add_block(self, data):
        # TODO 3: link the new block to the latest one, then store its hash.
        last = self.blocks[-1]
        block = Block(last.index + 1, data, last.hash)
        block.mine(self.difficulty)
        self.blocks.append(block)
        return block

    def is_valid(self, verbose=False):
        # TODO 4: read-only check. It never rewrites a hash, so it cannot
        # "fix" a tampered chain by accident. Returns False at the first
        # problem; verbose=True prints which rule failed.
        def fail(reason):
            if verbose:
                print("    reason:", reason)
            return False

        # Genesis was not mined: compare it with its expected original contents.
        expected_genesis_hash = Block(0, "Genesis", "0", timestamp=0).calculate_hash()
        genesis = self.blocks[0]
        if (genesis.calculate_hash() != expected_genesis_hash
                or genesis.hash != expected_genesis_hash):
            return fail("genesis block differs from its original contents")

        target = "0" * self.difficulty
        for i in range(1, len(self.blocks)):
            previous = self.blocks[i - 1]
            current = self.blocks[i]
            if current.previous_hash != previous.hash:
                return fail(f"block {i}: previous_hash does not match the hash "
                            f"of block {i - 1} (broken link)")
            if current.hash != current.calculate_hash():
                return fail(f"block {i}: stored hash does not match a fresh "
                            f"calculation (its data changed)")
            if not current.hash.startswith(target):
                return fail(f"block {i}: hash does not start with "
                            f"{self.difficulty} zero(s) (PoW rule)")
        return True


# ===========================================================================
# Helpers for the demonstrations
# ===========================================================================

def header(text):
    print()
    print("=" * 70)
    print(text)
    print("=" * 70)


def bits_changed(hex_a, hex_b):
    """How many of the 256 bits differ between two SHA-256 digests."""
    return bin(int(hex_a, 16) ^ int(hex_b, 16)).count("1")


def show_chain(chain):
    for block in chain.blocks:
        print(f"  #{block.index}  prev={block.previous_hash[:12]:<12}  "
              f"hash={block.hash[:12]}  nonce={block.nonce:<5}  data={block.data!r}")


def check(label, chain):
    """Print the result of is_valid() with the reason when it fails."""
    print(f"  {label} {chain.is_valid()}")
    if not chain.is_valid():
        chain.is_valid(verbose=True)


# ===========================================================================
# Exercise 1 - What changes when data changes?
# ===========================================================================

def exercise_1():
    header("Exercise 1 - What changes when data changes?")
    original = "Alice pays Bob 10 tokens"
    modified = "Alice pays Bob 100 tokens"
    d_original = sha256(original)
    d_modified = sha256(modified)

    print(f"  {original!r:<30} {d_original}")
    print(f"  {modified!r:<30} {d_modified}")
    print(f"  bits changed: {bits_changed(d_original, d_modified)} / 256, "
          f"hex characters changed: "
          f"{sum(a != b for a, b in zip(d_original, d_modified))} / 64")

    print("\n  Same text, run twice:")
    print(f"  run 1: {sha256(original)}")
    print(f"  run 2: {sha256(original)}")
    print(f"  identical: {sha256(original) == sha256(original)}")

    print("\n  Prediction: capitalization or spacing changes give a new digest.")
    variants = [
        "alice pays Bob 10 tokens",    # lower-case a
        "ALICE PAYS BOB 10 TOKENS",    # all capitals
        "Alice pays Bob 10 tokens ",   # trailing space
        "Alice  pays Bob 10 tokens",   # double space
    ]
    for text in variants:
        digest = sha256(text)
        print(f"  {text!r:<30} {digest[:16]}...  same as original: "
              f"{digest == d_original}  bits changed: {bits_changed(d_original, digest)}")


# ===========================================================================
# Exercise 2 - Design a block (Appendix B, Test A)
# ===========================================================================

def exercise_2():
    header("Exercise 2 - Design a block (Test A)")
    b1 = Block(1, "Alice -> Bob: 10", "abc", timestamp=0)
    b2 = Block(1, "Alice -> Bob: 10", "abc", timestamp=0)
    print(f"  string hashed for b1: {b1.index}|{b1.timestamp}|{b1.data}|"
          f"{b1.previous_hash}|{b1.nonce}")
    print(f"  b1 hash: {b1.calculate_hash()}")
    print(f"  b2 hash: {b2.calculate_hash()}")
    print("  same fields:", b1.calculate_hash() == b2.calculate_hash())
    b2.data = "Alice -> Bob: 100"
    print(f"  b2 hash after data change: {b2.calculate_hash()}")
    print("  changed data:", b1.calculate_hash() != b2.calculate_hash())


# ===========================================================================
# Exercise 3 - Make a chain and detect tampering (Appendix B, Test B)
# ===========================================================================

def exercise_3():
    header("Exercise 3 - Make a chain and detect tampering (Test B)")
    chain = Blockchain()  # no mining yet
    chain.add_block("Alice -> Bob: 10")
    chain.add_block("Bob -> Cara: 3")

    print("  Part A - chain built:")
    show_chain(chain)

    print("\n  Part C - attack:")
    check("before:", chain)                        # step 13
    chain.blocks[1].data = "Alice -> Bob: 100"     # step 14, hash NOT updated
    check("after: ", chain)                        # step 15

    print("\n  Step 16 (optional) - also recalculate block 1's hash:")
    chain.blocks[1].hash = chain.blocks[1].calculate_hash()
    check("after recalculating block 1:", chain)


# ===========================================================================
# Exercise 4 - Proof-of-Work (Appendix B, Test C)
# ===========================================================================

def exercise_4():
    header("Exercise 4 - Mine a block with Proof-of-Work (Test C)")
    print("  Observation table (Test C):")
    print(f"  {'difficulty':>10} | {'nonce found':>11} | {'elapsed (s)':>11} | hash prefix")
    for difficulty in (2, 3, 4):
        block = Block(1, "Alice -> Bob: 10", "abc", timestamp=0)
        start = time.perf_counter()
        block.mine(difficulty)
        duration = time.perf_counter() - start
        print(f"  {difficulty:>10} | {block.nonce:>11} | {duration:>11.4f} | {block.hash[:12]}")

    print("\n  Step 20 - repeated runs, 5 fresh blocks per difficulty")
    print("  (timestamp 1..5, so every block has different content):")
    for difficulty in (2, 3, 4):
        nonces, times = [], []
        for run in range(1, 6):
            block = Block(1, "Alice -> Bob: 10", "abc", timestamp=run)
            start = time.perf_counter()
            block.mine(difficulty)
            times.append(time.perf_counter() - start)
            nonces.append(block.nonce)
        print(f"  difficulty {difficulty}: nonces {nonces}")
        print(f"  {'':>13} times  {[round(t, 4) for t in times]}  "
              f"(expected about {16 ** difficulty} attempts on average)")

    print("\n  Step 21 - extension: a mined chain (difficulty 3)")
    chain = Blockchain(difficulty=3)
    chain.add_block("Alice -> Bob: 10")
    chain.add_block("Bob -> Cara: 3")
    show_chain(chain)
    check("valid:", chain)

    print("\n  Attacker changes block 1, then tries to cover it up:")
    attack = copy.deepcopy(chain)
    attack.blocks[1].data = "Alice -> Bob: 100"
    attack.blocks[1].hash = attack.blocks[1].calculate_hash()
    check("[1] recalculate block 1's hash:", attack)

    attack.blocks[1].mine(attack.difficulty)
    check("[2] re-mine block 1 only:", attack)

    attack.blocks[2].previous_hash = attack.blocks[1].hash
    attack.blocks[2].mine(attack.difficulty)
    check("[3] re-mine block 1 AND block 2:", attack)
    print("      -> one local copy can be fully rewritten (see Q5).")


# ===========================================================================
# Debugging challenge - find and justify one validation error
# ===========================================================================

def buggy_is_valid(chain):
    """A validator that only checks the links. It contains a bug."""
    for i in range(1, len(chain.blocks)):
        if chain.blocks[i].previous_hash != chain.blocks[i - 1].hash:
            return False
    return True


def debugging_challenge():
    header("Debugging challenge - a validator that only checks links")
    chain = Blockchain()
    chain.add_block("Alice -> Bob: 10")
    chain.add_block("Bob -> Cara: 3")
    chain.blocks[1].data = "Alice -> Bob: 100"     # stored hashes untouched

    print("  block 1 data changed to 'Alice -> Bob: 100', hashes left as they were")
    print(f"  buggy_is_valid(chain): {buggy_is_valid(chain)}   <- accepts the forgery")
    check("chain.is_valid():     ", chain)
    print("  Bug: buggy_is_valid compares two STORED values (previous_hash and")
    print("  hash). Nobody recomputes block 1's hash from its data, so the edit")
    print("  is invisible. Fix: also require block.hash == block.calculate_hash().")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    debugging_challenge()
