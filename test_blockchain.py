"""Automated checks for blockchain.py. Run with:  python -m unittest -v"""

import copy
import unittest

from blockchain import Block, Blockchain, buggy_is_valid, sha256


def demo_chain(difficulty=0):
    chain = Blockchain(difficulty)
    chain.add_block("Alice -> Bob: 10")
    chain.add_block("Bob -> Cara: 3")
    return chain


class HashTests(unittest.TestCase):
    def test_known_sha256_value(self):
        self.assertEqual(
            sha256("abc"),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        )

    def test_one_character_changes_the_digest(self):
        self.assertNotEqual(sha256("Alice pays Bob 10 tokens"),
                            sha256("Alice pays Bob 100 tokens"))


class BlockTests(unittest.TestCase):
    def test_a_identical_blocks_identical_hashes(self):
        b1 = Block(1, "Alice -> Bob: 10", "abc", timestamp=0)
        b2 = Block(1, "Alice -> Bob: 10", "abc", timestamp=0)
        self.assertEqual(b1.calculate_hash(), b2.calculate_hash())
        b2.data = "Alice -> Bob: 100"
        self.assertNotEqual(b1.calculate_hash(), b2.calculate_hash())

    def test_every_field_is_hashed(self):
        base = Block(1, "x", "abc", timestamp=0)
        for field, value in [("index", 2), ("timestamp", 1), ("data", "y"),
                             ("previous_hash", "abd"), ("nonce", 1)]:
            other = Block(1, "x", "abc", timestamp=0)
            setattr(other, field, value)
            self.assertNotEqual(base.calculate_hash(), other.calculate_hash(), field)

    def test_stored_hash_is_not_hashed(self):
        block = Block(1, "x", "abc", timestamp=0)
        before = block.calculate_hash()
        block.hash = "anything"
        self.assertEqual(before, block.calculate_hash())

    def test_c_mining_meets_difficulty(self):
        for difficulty in (2, 3):
            block = Block(1, "Alice -> Bob: 10", "abc", timestamp=0)
            block.mine(difficulty)
            self.assertTrue(block.hash.startswith("0" * difficulty))
            self.assertEqual(block.hash, block.calculate_hash())


class ChainTests(unittest.TestCase):
    def test_b_validate_then_tamper(self):
        chain = demo_chain()
        self.assertTrue(chain.is_valid())
        chain.blocks[1].data = "Alice -> Bob: 100"
        self.assertFalse(chain.is_valid())

    def test_links_point_to_previous_hash(self):
        chain = demo_chain()
        for i in range(1, len(chain.blocks)):
            self.assertEqual(chain.blocks[i].previous_hash, chain.blocks[i - 1].hash)
            self.assertEqual(chain.blocks[i].index, i)

    def test_recalculated_hash_breaks_next_link(self):
        chain = demo_chain()
        chain.blocks[1].data = "Alice -> Bob: 100"
        chain.blocks[1].hash = chain.blocks[1].calculate_hash()
        self.assertFalse(chain.is_valid())

    def test_tampered_genesis_is_detected(self):
        chain = demo_chain()
        chain.blocks[0].data = "Fake genesis"
        chain.blocks[0].hash = chain.blocks[0].calculate_hash()
        chain.blocks[1].previous_hash = chain.blocks[0].hash
        chain.blocks[1].hash = chain.blocks[1].calculate_hash()
        chain.blocks[2].previous_hash = chain.blocks[1].hash
        chain.blocks[2].hash = chain.blocks[2].calculate_hash()
        self.assertFalse(chain.is_valid())

    def test_validator_does_not_repair_tampering(self):
        chain = demo_chain()
        chain.blocks[1].data = "Alice -> Bob: 100"
        chain.is_valid()
        self.assertFalse(chain.is_valid())

    def test_mined_chain_is_valid_and_checks_pow(self):
        chain = demo_chain(difficulty=2)
        self.assertTrue(chain.is_valid())
        for block in chain.blocks[1:]:
            self.assertTrue(block.hash.startswith("00"))
        # Recomputing the hash without mining breaks the PoW rule.
        chain.blocks[1].data = "Alice -> Bob: 100"
        chain.blocks[1].hash = chain.blocks[1].calculate_hash()
        self.assertFalse(chain.blocks[1].hash.startswith("00"))
        self.assertFalse(chain.is_valid())

    def test_full_rewrite_passes_locally(self):
        chain = demo_chain(difficulty=2)
        chain.blocks[1].data = "Alice -> Bob: 100"
        chain.blocks[1].mine(2)
        chain.blocks[2].previous_hash = chain.blocks[1].hash
        chain.blocks[2].mine(2)
        self.assertTrue(chain.is_valid())


class DebuggingChallengeTests(unittest.TestCase):
    def test_link_only_validator_misses_the_edit(self):
        chain = demo_chain()
        tampered = copy.deepcopy(chain)
        tampered.blocks[1].data = "Alice -> Bob: 100"
        self.assertTrue(buggy_is_valid(tampered))
        self.assertFalse(tampered.is_valid())


if __name__ == "__main__":
    unittest.main()
