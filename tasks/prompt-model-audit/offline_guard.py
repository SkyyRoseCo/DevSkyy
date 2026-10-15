"""Pytest plugin: block real HTTP while permitting explicit httpx.MockTransport.

Use: PYTHONPATH=tasks/prompt-model-audit:$PWD .venv/bin/python -m pytest -p offline_guard ...
"""

import httpx
import pytest
import requests


@pytest.fixture(autouse=True)
def offline_http(monkeypatch):
    original_sync = httpx.Client.send
    original_async = httpx.AsyncClient.send

    def sync_send(client, *args, **kwargs):
        if not isinstance(client._transport, httpx.MockTransport):
            raise AssertionError("Live HTTP blocked by offline audit test guard")
        return original_sync(client, *args, **kwargs)

    async def async_send(client, *args, **kwargs):
        if not isinstance(client._transport, httpx.MockTransport):
            raise AssertionError("Live HTTP blocked by offline audit test guard")
        return await original_async(client, *args, **kwargs)

    def blocked(*args, **kwargs):
        raise AssertionError("Live HTTP blocked by offline audit test guard")

    monkeypatch.setattr(httpx.Client, "send", sync_send)
    monkeypatch.setattr(httpx.AsyncClient, "send", async_send)
    monkeypatch.setattr(requests.Session, "send", blocked)
