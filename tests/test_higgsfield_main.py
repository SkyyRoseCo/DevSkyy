"""Offline tests for the Higgsfield Seedance 2.5 example (repo-root main.py).

The SDK's subscribe() is replaced with a fake, so no request is made and nothing
is billed. Credentials come from a tmp_path .env file, never the real .env.local.
"""

import importlib.util
import sys
from pathlib import Path

import higgsfield_client
import pytest

_SPEC = importlib.util.spec_from_file_location(
    "higgsfield_main",
    Path(__file__).resolve().parent.parent / "main.py",
)
higgsfield_main = importlib.util.module_from_spec(_SPEC)
sys.modules["higgsfield_main"] = higgsfield_main
_SPEC.loader.exec_module(higgsfield_main)

FAKE_KEY = "test-key-id:test-key-secret"
VIDEO_URL = "https://cdn.example.test/seedance/out.mp4"


@pytest.fixture
def clean_env(monkeypatch):
    # setenv first so teardown removes whatever load_dotenv writes later.
    monkeypatch.setenv("HF_KEY", "placeholder")
    monkeypatch.delenv("HF_KEY")
    return monkeypatch


@pytest.fixture
def env_file(tmp_path, clean_env):
    path = tmp_path / ".env.local"
    path.write_text(f"HF_KEY={FAKE_KEY}\n")
    clean_env.setattr(higgsfield_main, "ENV_FILE", path)
    # pytest has no TTY, so the money gate aborts unless the batch opt-in is set.
    # The gate's own tests remove it again.
    clean_env.setenv("SKYYROSE_AUTO_CONFIRM", "1")
    return path


def fake_subscribe(payload, final_status, calls):
    def subscribe(application, arguments, *, on_enqueue=None, on_queue_update=None):
        calls.append((application, arguments))
        on_enqueue("req-123")
        on_queue_update(higgsfield_client.Queued())
        on_queue_update(higgsfield_client.InProgress())
        on_queue_update(final_status)
        return payload

    return subscribe


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, False),
        ("", False),
        ("no-separator", False),
        (":secret-only", False),
        ("id-only:", False),
        ("key-id:key-secret", True),
    ],
)
def test_credentials_configured(clean_env, value, expected):
    if value is not None:
        clean_env.setenv("HF_KEY", value)
    assert higgsfield_main.credentials_configured() is expected


@pytest.mark.parametrize(
    "video",
    [{"url": VIDEO_URL}, [{"url": VIDEO_URL}]],
)
def test_extract_video_url_completed(video):
    assert higgsfield_main.extract_video_url({"status": "completed", "video": video}) == VIDEO_URL


@pytest.mark.parametrize(
    ("status", "reason"),
    [
        ("failed", "failed"),
        ("nsfw", "content moderation"),
        ("canceled", "canceled"),
        ("in_progress", "unexpected status"),
        (None, "unexpected status"),
    ],
)
def test_extract_video_url_rejects_non_completed(status, reason):
    payload = {"status": status, "video": {"url": VIDEO_URL}}
    with pytest.raises(higgsfield_main.GenerationError, match=reason):
        higgsfield_main.extract_video_url(payload)


@pytest.mark.parametrize(
    "payload",
    [
        {"status": "completed"},
        {"status": "completed", "video": {}},
        {"status": "completed", "video": []},
        {"status": "completed", "video": {"url": "not-a-url"}},
        {"status": "completed", "video": {"url": "ftp://host/out.mp4"}},
    ],
)
def test_extract_video_url_rejects_missing_url(payload):
    with pytest.raises(higgsfield_main.GenerationError, match="no video URL"):
        higgsfield_main.extract_video_url(payload)


def test_main_success_prints_only_url(env_file, monkeypatch, capsys):
    calls = []
    payload = {"status": "completed", "request_id": "req-123", "video": {"url": VIDEO_URL}}
    monkeypatch.setattr(
        higgsfield_client,
        "subscribe",
        fake_subscribe(payload, higgsfield_client.Completed(), calls),
    )

    assert higgsfield_main.main() == 0

    out, err = capsys.readouterr()
    assert out == f"{VIDEO_URL}\n"
    assert calls == [(higgsfield_main.MODEL, higgsfield_main.ARGUMENTS)]
    assert calls[0][1] == {
        "prompt": "A cinematic scene at sunset",
        "duration": 5,
        "resolution": "720p",
        "aspect_ratio": "16:9",
    }
    assert FAKE_KEY not in out + err
    assert "test-key-secret" not in out + err


@pytest.mark.parametrize(
    ("status_value", "status_obj", "reason"),
    [
        ("failed", higgsfield_client.Failed(), "failed"),
        ("nsfw", higgsfield_client.NSFW(), "content moderation"),
        ("canceled", higgsfield_client.Cancelled(), "canceled"),
    ],
)
def test_main_terminal_failures_exit_nonzero(
    env_file, monkeypatch, capsys, status_value, status_obj, reason
):
    payload = {"status": status_value, "request_id": "req-123"}
    monkeypatch.setattr(higgsfield_client, "subscribe", fake_subscribe(payload, status_obj, []))

    assert higgsfield_main.main() == 1

    out, err = capsys.readouterr()
    assert out == ""
    assert reason in err
    assert "req-123" in err
    assert "test-key-secret" not in err


def test_main_rejects_completed_payload_when_polled_status_disagrees(env_file, monkeypatch, capsys):
    payload = {"status": "completed", "video": {"url": VIDEO_URL}}
    monkeypatch.setattr(
        higgsfield_client, "subscribe", fake_subscribe(payload, higgsfield_client.Failed(), [])
    )

    assert higgsfield_main.main() == 1
    assert capsys.readouterr().out == ""


def test_main_missing_credentials_never_calls_api(tmp_path, clean_env, capsys):
    clean_env.setattr(higgsfield_main, "ENV_FILE", tmp_path / "absent.env")
    calls = []
    clean_env.setattr(
        higgsfield_client, "subscribe", fake_subscribe({}, higgsfield_client.Completed(), calls)
    )

    assert higgsfield_main.main() == 2
    assert calls == []
    out, err = capsys.readouterr()
    assert out == ""
    assert "HF_KEY is missing" in err


def test_main_api_error_exits_nonzero(env_file, monkeypatch, capsys):
    def failing_subscribe(*args, **kwargs):
        raise higgsfield_client.HiggsfieldClientError("Insufficient credits")

    monkeypatch.setattr(higgsfield_client, "subscribe", failing_subscribe)

    assert higgsfield_main.main() == 3
    out, err = capsys.readouterr()
    assert out == ""
    assert "Insufficient credits" in err


def test_watcher_times_out_only_while_not_done():
    watcher = higgsfield_main.ProgressWatcher(max_wait_seconds=-1)
    watcher.on_queue_update(higgsfield_client.Completed())
    with pytest.raises(TimeoutError):
        watcher.on_queue_update(higgsfield_client.InProgress())


class TestMoneyGate:
    """Every run is billable, so nothing is submitted without an explicit yes."""

    @pytest.fixture
    def calls(self, env_file, monkeypatch):
        recorded = []
        payload = {"status": "completed", "video": {"url": VIDEO_URL}}
        monkeypatch.setattr(
            higgsfield_client,
            "subscribe",
            fake_subscribe(payload, higgsfield_client.Completed(), recorded),
        )
        monkeypatch.delenv("SKYYROSE_AUTO_CONFIRM")
        return recorded

    def test_no_tty_and_no_opt_in_never_submits(self, calls, capsys):
        # No overrides at all: this exercises the production default TTY probe.
        assert higgsfield_main.main() == higgsfield_main.EXIT_NOT_CONFIRMED
        assert calls == []
        out, err = capsys.readouterr()
        assert out == ""
        assert "SKYYROSE_AUTO_CONFIRM" in err

    def test_manifest_is_shown_before_the_decision(self, calls, capsys):
        higgsfield_main.main(is_tty=lambda: False)
        err = capsys.readouterr().err
        assert "STOP" in err
        assert higgsfield_main.MODEL in err
        assert "720p" in err
        assert "billable" in err.lower()

    @pytest.mark.parametrize("value", ["true", "yes", "0", "", " 1"])
    def test_opt_in_must_be_exactly_one(self, calls, monkeypatch, value):
        monkeypatch.setenv("SKYYROSE_AUTO_CONFIRM", value)
        assert higgsfield_main.main(is_tty=lambda: False) == higgsfield_main.EXIT_NOT_CONFIRMED
        assert calls == []

    def test_opt_in_proceeds_without_a_tty(self, calls, monkeypatch, capsys):
        monkeypatch.setenv("SKYYROSE_AUTO_CONFIRM", "1")
        assert higgsfield_main.main(is_tty=lambda: False) == 0
        assert len(calls) == 1
        assert "STOP" in capsys.readouterr().err

    @pytest.mark.parametrize("answer", ["y", "Y", " yes "])
    def test_tty_yes_proceeds(self, calls, answer):
        assert higgsfield_main.main(prompt_fn=lambda _: answer, is_tty=lambda: True) == 0
        assert len(calls) == 1

    @pytest.mark.parametrize("answer", ["", "n", "no", "yeah", "1"])
    def test_tty_anything_else_aborts(self, calls, answer):
        code = higgsfield_main.main(prompt_fn=lambda _: answer, is_tty=lambda: True)
        assert code == higgsfield_main.EXIT_NOT_CONFIRMED
        assert calls == []

    def test_closed_stdin_is_not_confirmation(self, calls):
        def closed(_):
            raise EOFError

        code = higgsfield_main.main(prompt_fn=closed, is_tty=lambda: True)
        assert code == higgsfield_main.EXIT_NOT_CONFIRMED
        assert calls == []

    def test_missing_credentials_still_wins_over_the_gate(self, tmp_path, clean_env):
        clean_env.setattr(higgsfield_main, "ENV_FILE", tmp_path / "absent.env")
        assert higgsfield_main.main(is_tty=lambda: False) == 2

    def test_env_file_cannot_grant_the_opt_in(self, calls, env_file, capsys):
        # The opt-in is read from the real environment before .env.local is loaded:
        # a line in the env file would otherwise auto-confirm every future run.
        env_file.write_text(f"HF_KEY={FAKE_KEY}\nSKYYROSE_AUTO_CONFIRM=1\n")

        assert higgsfield_main.main(is_tty=lambda: False) == higgsfield_main.EXIT_NOT_CONFIRMED
        assert calls == []
        assert "STOP" in capsys.readouterr().err
