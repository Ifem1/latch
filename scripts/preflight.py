#!/usr/bin/env python3
"""Repository-level preflight that does not need GenLayer packages installed."""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = [ROOT / "contracts" / "latch.py", ROOT / "contracts" / "example_consumer.py"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    errors: list[str] = []
    all_text = "\n".join(path.read_text(encoding="utf-8") for path in ROOT.rglob("*") if path.is_file() and path.suffix in {".py", ".md", ".yaml", ".yml", ".txt"})

    cfg = (ROOT / "gltest.config.yaml").read_text(encoding="utf-8")
    if "https://studio.genlayer.com/api" not in cfg:
        errors.append("gltest.config.yaml does not point to stable Studionet RPC")

    for path in CONTRACTS:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            errors.append(f"syntax error in {path.name}: {exc}")
        if path.stat().st_size > 64_000:
            errors.append(f"{path.name} is unexpectedly large ({path.stat().st_size} bytes)")

    latch_text = CONTRACTS[0].read_text(encoding="utf-8")
    for needle in [
        "run_nondet_unsafe",
        "ILatchConsumer",
        "STATE_COMMITTED",
        "STATE_REVERT_REQUIRED",
        "expire_latch",
        "acknowledge_terminal",
        "on=\"finalized\"",
    ]:
        if needle not in latch_text:
            errors.append(f"latch.py missing required mechanism marker: {needle}")

    if errors:
        for err in errors:
            print("ERROR:", err)
        raise SystemExit(1)

    print("Static preflight: PASS")
    for path in CONTRACTS:
        print(f"{path.relative_to(ROOT)}  bytes={path.stat().st_size}  sha256={sha256(path)}")
    print("Network target: Studionet / 61999 only")


if __name__ == "__main__":
    main()
