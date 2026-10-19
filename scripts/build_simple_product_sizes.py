#!/usr/bin/env python3
"""Build/check the generated V2 simple-size projection, never product facts."""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from skyyrose.core.simple_product_sizes import reconcile  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    drift = reconcile(args.check)
    for path in drift:
        print(("STALE " if args.check else "UPDATED ") + path)
    if not drift:
        print("PASS: V2 exact string sizes match get_product and the canonical registry")
    return int(args.check and bool(drift))


if __name__ == "__main__":
    raise SystemExit(main())
