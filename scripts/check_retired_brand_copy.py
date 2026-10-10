"""Reject retired brand copy without storing the removed wording in the repository."""
from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path

# Fingerprint of the founder-retired wording, normalized to ASCII letters.
# A digest keeps the prohibited copy itself out of source, tests, and logs.
RETIRED_DIGEST = '19a498e50c9f1ddeb3557f71df88ffd86160dc1c2c7f23ab98c729edf97a515f'
RETIRED_LENGTH = 23


def contains_retired_copy(text: str) -> bool:
    """Match case, punctuation, whitespace, markup, and hashtag variants."""
    text = re.sub(r'<[^>]*>', '', text)
    normalized = re.sub(r'[^a-z]', '', text.lower())
    windows = re.finditer(rf"(?=(l[a-z]{{{RETIRED_LENGTH - 2}}}e))", normalized)
    return any(
        hashlib.sha256(match.group(1).encode()).hexdigest() == RETIRED_DIGEST
        for match in windows
    )


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    paths = subprocess.check_output(
        ['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=root
    ).decode().split('\0')
    failures = []
    for name in sorted(set(paths)):
        path = root / name
        if not name or not path.is_file() or path.is_symlink():
            continue
        try:
            data = path.read_bytes()
            if b'\0' in data:
                continue
            text = data.decode('utf-8')
        except (UnicodeError, OSError):
            continue
        if contains_retired_copy(text) or contains_retired_copy(name):
            failures.append(name)
    for name in failures:
        print(f'Retired brand copy must be removed: {name}')
    print(f'Retired-copy check: {len(failures)} violating files')
    return int(bool(failures))


if __name__ == '__main__':
    raise SystemExit(main())
