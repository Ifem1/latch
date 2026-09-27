#!/usr/bin/env python3
"""Print source hashes to pin the exact code reviewed/deployed."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "contracts/latch.py",
    "contracts/example_consumer.py",
    "README.md",
    "SECURITY.md",
    "SUBMISSION.md",
]

manifest = {}
for rel in FILES:
    p = ROOT / rel
    if p.exists():
        manifest[rel] = {
            "bytes": p.stat().st_size,
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        }
print(json.dumps(manifest, indent=2, sort_keys=True))
