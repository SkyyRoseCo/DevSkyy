"""Tests for scripts/check_anthropic_key.py - no network, no real credentials."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import anthropic
import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_anthropic_key.py"
FAKE_KEY = "sk-ant-fake-0123456789abcdef"
ENV_VARS = ("ANTHROPIC_API_KEY", "ANTHROPIC_BASE_URL", "ANTHROPIC_AUTH_TOKEN")


@pytest.fixture
def mod(monkeypatch, tmp_path):
    spec = importlib.util.spec_from_file_location("check_anthropic_key", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    for var in ENV_VARS:
        monkeypatch.delenv(var, raising=False)
    return module


@pytest.fixture
def fake(monkeypatch):
    calls = SimpleNamespace(kwargs=[], messages=0)

    class FakeClient:
        def __init__(self, **kwargs):
            calls.kwargs.append(kwargs)
            self.models = SimpleNamespace(
                list=lambda limit=5: SimpleNamespace(data=[SimpleNamespace(id="m1")])
            )
            self.messages = SimpleNamespace(create=self._create)

        def _create(self, **_):
            calls.messages += 1
            raise AssertionError("messages.create must not be called")

    monkeypatch.setattr(anthropic, "Anthropic", FakeClient)
    return calls


def run(mod, monkeypatch, *argv):
    monkeypatch.setattr("sys.argv", ["check_anthropic_key.py", *argv])
    try:
        return mod.main()
    except SystemExit as exc:
        return exc.code


def test_base_url_pinned_and_key_passed(mod, fake, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    assert run(mod, monkeypatch) == 0
    assert fake.kwargs == [{"api_key": FAKE_KEY, "base_url": "https://api.anthropic.com"}]


def test_trailing_slash_base_url_tolerated(mod, fake, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com/")
    assert run(mod, monkeypatch) == 0
    assert fake.kwargs[0]["base_url"] == "https://api.anthropic.com"


def test_foreign_base_url_refused_before_client(mod, fake, monkeypatch, capsys):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://evil.example.com")
    code = run(mod, monkeypatch)
    assert code and code != 0
    assert fake.kwargs == []
    assert "unverified endpoint" in str(code)
    out = capsys.readouterr()
    assert FAKE_KEY not in out.out + out.err + str(code)


def test_auth_token_refused(mod, fake, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    monkeypatch.setenv("ANTHROPIC_AUTH_TOKEN", "tok-fake")
    code = run(mod, monkeypatch)
    assert code and code != 0
    assert fake.kwargs == []
    assert "tok-fake" not in str(code)


def test_env_file_other_vars_not_exported(mod, fake, monkeypatch, tmp_path):
    (tmp_path / ".env").write_text(
        f"ANTHROPIC_API_KEY={FAKE_KEY}\nUNRELATED_SECRET_VAR=hunter2\nANTHROPIC_BASE_URL=https://evil.example.com\n"
    )
    assert run(mod, monkeypatch) == 0
    import os

    assert "UNRELATED_SECRET_VAR" not in os.environ
    assert "ANTHROPIC_BASE_URL" not in os.environ
    assert "ANTHROPIC_API_KEY" not in os.environ
    assert fake.kwargs[0]["api_key"] == FAKE_KEY


def test_precedence_shell_then_env_then_env_local(mod, fake, monkeypatch, tmp_path):
    (tmp_path / ".env").write_text("ANTHROPIC_API_KEY=sk-ant-from-env\n")
    (tmp_path / ".env.local").write_text("ANTHROPIC_API_KEY=sk-ant-from-local\n")
    assert run(mod, monkeypatch) == 0
    assert fake.kwargs[-1]["api_key"] == "sk-ant-from-env"
    (tmp_path / ".env").write_text("OTHER=1\n")
    assert run(mod, monkeypatch) == 0
    assert fake.kwargs[-1]["api_key"] == "sk-ant-from-local"
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    assert run(mod, monkeypatch) == 0
    assert fake.kwargs[-1]["api_key"] == FAKE_KEY


def test_missing_key_clean_fail(mod, fake, monkeypatch):
    code = run(mod, monkeypatch)
    assert code and code != 0
    assert "no ANTHROPIC_API_KEY" in str(code)
    assert fake.kwargs == []


def test_key_never_printed(mod, fake, monkeypatch, capsys):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    assert run(mod, monkeypatch) == 0
    out = capsys.readouterr()
    assert FAKE_KEY not in out.out + out.err


def test_message_without_yes_refused(mod, fake, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    code = run(mod, monkeypatch, "--message")
    assert code and code != 0
    assert "STOP" in str(code)
    assert fake.kwargs == []
    assert fake.messages == 0
