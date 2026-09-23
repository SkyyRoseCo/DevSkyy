"""Real Space components and callback, with all HTTP replaced by local fakes."""

import base64
import importlib.util
import io
import os
import runpy
import socket
from pathlib import Path

os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
os.environ["HF_HUB_OFFLINE"] = "1"

import gradio as gr
import pytest
from gradio.data_classes import ImageData
from PIL import Image

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


@pytest.fixture(autouse=True)
def forbid_network(monkeypatch):
    def reject(*args, **kwargs):
        raise AssertionError("Network access is forbidden in offline Space tests")

    monkeypatch.setattr(socket.socket, "connect", reject)


@pytest.fixture
def space():
    spec = importlib.util.spec_from_file_location("virtual_tryon_space", APP_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_real_components_and_image_roundtrip(space, tmp_path):
    app = space.create_app()
    images = [block for block in app.blocks.values() if isinstance(block, gr.Image)]
    assert [image.label for image in images] == [
        "Upload Your Photo",
        "Select Product Image",
        "Result",
    ]
    assert all(image.type == "pil" for image in images)
    path = tmp_path / "synthetic.png"
    Image.new("RGB", (8, 12), "red").save(path)
    value = images[0].preprocess(ImageData(path=str(path)))
    assert isinstance(value, Image.Image)
    assert value.size == (8, 12)
    result = images[2].postprocess(value)
    assert Image.open(result.path).size == (8, 12)
    callback = next(fn for fn in app.fns.values() if fn.fn is space.virtual_tryon)
    assert len(callback.inputs) == 4
    assert callback.outputs == [images[2]]


def test_main_passes_theme_to_launch(monkeypatch):
    calls = []
    monkeypatch.setattr(gr.Blocks, "launch", lambda self, **kwargs: calls.append(kwargs))
    runpy.run_path(str(APP_PATH), run_name="__main__")
    assert len(calls) == 1
    assert isinstance(calls[0]["theme"], gr.themes.Soft)
    assert calls[0]["theme"].primary_500 == gr.themes.colors.rose.c500
    assert calls[0]["theme"].secondary_500 == gr.themes.colors.stone.c500
    assert calls[0]["server_port"] == 7860
    assert calls[0]["share"] is False


def test_submit_callback_uses_real_encoding_and_fake_http(space, monkeypatch):
    output = io.BytesIO()
    Image.new("RGB", (16, 24), "blue").save(output, format="PNG")
    calls = []

    class Response:
        status = 200

        def __init__(self, payload=None):
            self.payload = payload

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def json(self):
            return self.payload

        async def read(self):
            return output.getvalue()

    class Session:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        def request(self, method, url, json):
            calls.append((method, url, json))
            if method == "POST":
                return Response({"id": "synthetic-prediction"})
            return Response(
                {"status": "succeeded", "output": ["https://example.invalid/result.png"]}
            )

        def get(self, url):
            assert url == "https://example.invalid/result.png"
            return Response()

    monkeypatch.setattr(space.aiohttp, "ClientSession", Session)
    monkeypatch.setattr(space, "FASHN_API_KEY", "synthetic-test-key")
    app = space.create_app()
    callback = next(fn.fn for fn in app.fns.values() if fn.fn is space.virtual_tryon)
    image = Image.new("RGB", (8, 12), "red")
    result = callback(image, image, "dresses", "quality")
    assert result.size == (16, 24)
    assert result.getpixel((0, 0)) == (0, 0, 255)
    assert [call[0] for call in calls] == ["POST", "GET"]
    payload = calls[0][2]
    assert payload["category"] == "dresses"
    assert payload["mode"] == "quality"
    encoded = payload["model_image"].split(",", 1)[1]
    assert Image.open(io.BytesIO(base64.b64decode(encoded))).size == (8, 12)
