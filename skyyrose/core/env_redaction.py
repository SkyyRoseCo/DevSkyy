"""Print env-file key names without printing secrets by accident.

bug-357: a session printed ~25 live credential VALUES into its transcript while
auditing `.env.secrets`, by printing `dotenv_values()` keys. "Names are safe,
only values are secret" holds for a well-formed env file and fails for one that
is not: `.env.secrets` carries prose and pasted-command lines shaped
``<label> = <secret>`` and ``Name: <secret>``, so python-dotenv parses the
SECRET as the dict key. A names-only print is then a values print.

Use these helpers for anything derived from a file you have not proven
well-formed. The rule is a WHITELIST — print a token only if it looks like an
env var name — because a blacklist of secret shapes can only ever enumerate the
prefixes someone thought of (``sk-``, ``ghp_``, ``hf_``), and the next vendor
picks a new one.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping

# Anchored on both ends deliberately: an unanchored pattern would match the
# name embedded in a pasted line like "Name: HF_TOKEN=hf_realsecret" and echo
# the whole line. `fullmatch` semantics via \A..\Z rather than ^..$, because
# $ also matches before a trailing newline and a multi-line token would slip
# its second line past the check.
ENV_NAME_RE = re.compile(r"\A[A-Z][A-Z0-9_]*\Z")

_REDACTED_PREFIX = "<redacted:"
_DIGEST_CHARS = 8


def redact_env_name(token: str) -> str:
    """Return `token` if it is an env var name, else a stable opaque label.

    The label carries a truncated digest so the same unprintable key is
    recognisable across two sightings — enough to say "this one again" while
    never revealing the material. It is not a security boundary against someone
    holding the plaintext, and is not meant to be: the threat here is a secret
    reaching a transcript, not an attacker reversing a hash.
    """
    if ENV_NAME_RE.match(token):
        return token
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()[:_DIGEST_CHARS]
    return f"{_REDACTED_PREFIX}{digest}>"


def safe_env_names(parsed: Mapping[str, object]) -> list[str]:
    """Map a `dotenv_values()` result to names that are safe to print.

    Order follows the input so the output still lines up with the file. Never
    iterate a parse result's keys directly into a log, a report or a message:
    that is the exact call that caused bug-357.
    """
    return [redact_env_name(str(key)) for key in parsed]
