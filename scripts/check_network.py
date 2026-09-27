#!/usr/bin/env python3
"""Hard guard that permits only stable GenLayer Studionet / chain 61999."""

import json
import sys
import urllib.request

RPC = "https://studio.genlayer.com/api"
EXPECTED_CHAIN_ID = 61999


def rpc(method, params=None):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params or []}).encode()
    req = urllib.request.Request(
        RPC,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "LATCH-network-check/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        data = json.load(response)
    if "error" in data:
        raise RuntimeError(data["error"])
    return data["result"]


def main():
    try:
        result = rpc("eth_chainId")
    except Exception as exc:
        print(f"RPC: {RPC}")
        raise SystemExit(
            f"REFUSING TO CONTINUE: unable to verify target chain ID ({type(exc).__name__}: {exc})"
        ) from exc
    chain_id = int(result, 16) if isinstance(result, str) and result.startswith("0x") else int(result)
    print(f"RPC: {RPC}")
    print(f"chain id: {chain_id}")
    if chain_id != EXPECTED_CHAIN_ID:
        raise SystemExit(f"REFUSING TO CONTINUE: expected Studionet {EXPECTED_CHAIN_ID}, got {chain_id}")
    print("OK: stable GenLayer Studionet / chain 61999")


if __name__ == "__main__":
    main()
