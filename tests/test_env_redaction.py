"""Never echo an env-file key without proving it is a key — RED first.

bug-357 (2026-09-21): a session printed ~25 live credential VALUES into its
transcript while auditing `.env.secrets`. It printed `dotenv_values()` KEYS on
the standing assumption that names are safe and only values are secret.

That invariant does not survive a malformed file. `.env.secrets` carries prose
and pasted-command lines shaped `<label> = <secret>` and `Name: <secret>`, so
python-dotenv parses the SECRET as the dict key. A names-only print is then a
values print.

The rule this encodes: use a WHITELIST, never a blacklist. A token is printable
only if it looks like an env var name; anything else becomes a stable hash so
two sightings can still be correlated, without ever showing the material.
"""

from __future__ import annotations

import pytest

from skyyrose.core.env_redaction import ENV_NAME_RE, redact_env_name, safe_env_names

# Lines shaped like the ones that caused bug-357. The VALUES here are invented;
# what matters is the shape python-dotenv sees.
MALFORMED_KEYS = [
    "sk-proj-AAAABBBBCCCCDDDDEEEEFFFF",  # a pasted secret became the key
    "Name: hf_XXXXXXXXXXXXXXXXXXXX",  # "Name: <secret>" prose line
    "OpenAI key = sk-live-1234567890",  # "<label> = <secret>" prose line
    "ghp_ZZZZZZZZZZZZZZZZZZZZZZZZZZ",
    "Bearer eyJhbGciOiJIUzI1NiJ9.payload.sig",
]
WELL_FORMED_KEYS = ["OPENAI_API_KEY", "HF_TOKEN", "AWS_SECRET_ACCESS_KEY", "A", "X2_Y"]


class TestWhitelist:
    @pytest.mark.parametrize("name", WELL_FORMED_KEYS)
    def test_real_env_names_are_printed_unchanged(self, name: str) -> None:
        assert redact_env_name(name) == name

    @pytest.mark.parametrize("token", MALFORMED_KEYS)
    def test_anything_that_is_not_a_name_is_never_echoed(self, token: str) -> None:
        out = redact_env_name(token)
        assert token not in out, "the raw token reached the output"
        # Any run of >=8 chars from the token would be a usable fragment.
        for start in range(0, max(1, len(token) - 8)):
            assert token[start : start + 8] not in out, "a fragment of the token leaked"

    @pytest.mark.parametrize("token", MALFORMED_KEYS)
    def test_redaction_is_stable_and_correlatable(self, token: str) -> None:
        """Two sightings of one unprintable key must match, without revealing it."""
        assert redact_env_name(token) == redact_env_name(token)
        assert redact_env_name(token) != redact_env_name(token + "x")

    def test_lowercase_and_leading_digit_are_not_names(self) -> None:
        for token in ("openai_api_key", "1KEY", "_KEY", "KEY-NAME", "KEY NAME"):
            assert redact_env_name(token) != token, f"{token!r} was echoed as a name"

    def test_the_pattern_is_anchored(self) -> None:
        """An unanchored pattern would match a name INSIDE a pasted secret."""
        assert not ENV_NAME_RE.match("Name: HF_TOKEN=hf_secret")
        assert not ENV_NAME_RE.match("PREFIX\nOPENAI_API_KEY")


class TestSafeEnvNames:
    def test_maps_a_whole_parse_result(self) -> None:
        parsed = {"OPENAI_API_KEY": "v", "sk-proj-AAAABBBBCCCC": "v", "HF_TOKEN": "v"}
        out = safe_env_names(parsed)
        assert out[0] == "OPENAI_API_KEY"
        assert out[2] == "HF_TOKEN"
        assert "sk-proj-AAAABBBBCCCC" not in " ".join(out)

    def test_output_order_follows_input(self) -> None:
        parsed = {"B_KEY": "1", "A_KEY": "2"}
        assert safe_env_names(parsed) == ["B_KEY", "A_KEY"]

    def test_empty_input_is_empty_output(self) -> None:
        assert safe_env_names({}) == []
