# TP1 - Understand a blockchain by building one

EFREI / Digital Finance, session 1. A simplified blockchain in Python: SHA-256 hashing,
hash-linked blocks, tamper detection and a small Proof-of-Work miner.

This is a teaching model (a Python list on one computer), not a decentralized network. It
demonstrates data integrity and the PoW idea, but not networking, signatures, distributed
agreement or adversarial security.

## Files

| File | Content |
|---|---|
| [blockchain.py](blockchain.py) | The completed Appendix A starter code (`Block`, `Blockchain`, every TODO) plus the demos for exercises 1 to 4, Appendix B tests A, B and C, and the debugging challenge |
| [ANSWERS.md](ANSWERS.md) | Written answers: prediction, Q1 to Q7, mining observation table, debugging challenge, dApp proposal |
| [console_log.txt](console_log.txt) | Console output of one run: a valid chain and failed tampering checks |
| [test_blockchain.py](test_blockchain.py) | Automated checks (`unittest`) |

## Run

Python 3.8 or later, standard library only.

```bash
python blockchain.py          # every exercise, about 1 second
python -m unittest -v         # automated tests
```

`blockchain.py` can also be pasted as-is into the Programiz online Python editor.
