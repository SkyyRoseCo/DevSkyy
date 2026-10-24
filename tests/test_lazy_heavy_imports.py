"""Cold-import and first-use contracts without model downloads or provider calls."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
pytestmark = pytest.mark.timeout(90)

_OFFLINE = """
import builtins, importlib, socket, sys
heavy = {'torch', 'transformers', 'sentence_transformers'}
attempts = []
original_import = builtins.__import__
def guarded_import(name, *args, **kwargs):
    if name.split('.')[0] in heavy:
        attempts.append(name)
        raise ImportError('Optional ML library blocked by offline test: ' + name)
    return original_import(name, *args, **kwargs)
builtins.__import__ = guarded_import
def no_network(*args, **kwargs):
    raise AssertionError('Network access is forbidden in import regression tests')
socket.socket.connect = no_network
"""


def _run(source: str) -> None:
    result = subprocess.run(
        [sys.executable, "-c", _OFFLINE + dedent(source)],
        # cwd= forces fork on macOS after native frameworks may be armed.
        # A PYTHONPATH-only child can use posix_spawn instead (bug-263).
        env={
            **os.environ,
            "PYTHONPATH": str(REPO_ROOT),
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            "OTEL_SDK_DISABLED": "true",
        },
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stdout[-1000:] + result.stderr[-4000:]


@pytest.mark.parametrize(
    "module",
    [
        "llm.evaluation_metrics",
        "llm.model_ids",
        "imagery.visual_comparison",
        "imagery.headless_renderer",
        "agents.analytics_agent",
    ],
)
def test_import_does_not_attempt_ml_imports(module: str) -> None:
    _run(f"""
        importlib.import_module({module!r})
        assert not attempts, attempts
        assert not heavy.intersection(sys.modules)
        """)


def test_import_agents_package_loads_no_agent_tree() -> None:
    _run("""
        import agents
        loaded = [name for name in sys.modules if name.startswith('agents.')]
        assert not loaded, loaded
        assert not attempts, attempts
        assert not {'llm', 'mcp', 'claude_agent_sdk', 'aiohttp', 'scipy', 'fastapi'}.intersection(sys.modules)
        """)


def test_exports_aliases_caching_and_submodule_access_with_offline_modules() -> None:
    _run("""
        import types
        from unittest.mock import patch
        import agents
        assert set(agents.__all__) == set(agents._LAZY_EXPORTS)
        modules = {}
        for module, attr in agents._LAZY_EXPORTS.values():
            target = modules.setdefault(module, types.SimpleNamespace())
            if not hasattr(target, attr):
                setattr(target, attr, object())
        def load(module, package=None):
            assert package == 'agents'
            return modules[module.removeprefix('.')]
        with patch.object(agents.importlib, 'import_module', side_effect=load) as loader:
            for name, (module, attr) in agents._LAZY_EXPORTS.items():
                expected = getattr(modules[module], attr)
                assert getattr(agents, name) is expected
                count = loader.call_count
                assert getattr(agents, name) is expected
                assert loader.call_count == count
            assert agents.TRIPO_BRAND_DNA is modules['tripo_agent'].SKYYROSE_BRAND_DNA
            assert agents.TripoGenerationResult is modules['tripo_agent'].GenerationResult
        with patch.object(agents.importlib, 'import_module', return_value=modules['core']) as loader:
            assert agents.core is modules['core']
            loader.assert_called_once_with('agents.core')
        assert 'AnalyticsAgent' in dir(agents)
        with patch.object(agents.importlib, 'import_module', side_effect=ImportError('offline optional dependency')):
            for name in ['does_not_exist', '_private_name']:
                try:
                    getattr(agents, name)
                except AttributeError:
                    pass
                else:
                    raise AssertionError(name + ' unexpectedly resolved')
        """)


def test_missing_optional_agent_exports_keep_existing_behavior() -> None:
    _run("""
        from unittest.mock import patch
        import agents
        with patch.object(agents.importlib, 'import_module', side_effect=ImportError('optional dependency missing')):
            assert agents.AnalyticsAgent is None
            try:
                agents.CoreAgent
            except AttributeError:
                pass
            else:
                raise AssertionError('CoreAgent must be absent when its module cannot load')
        """)


def test_sentence_model_loads_on_first_use_and_reuses_the_initialized_instance() -> None:
    _run("""
        import asyncio, types
        import numpy as np
        metrics = importlib.import_module('llm.evaluation_metrics')
        calls = []
        class OfflineEncoder:
            def __init__(self, model_name):
                calls.append(model_name)
            def encode(self, sentences):
                return np.ones((len(sentences), 2))
        sys.modules['sentence_transformers'] = types.SimpleNamespace(SentenceTransformer=OfflineEncoder)
        builtins.__import__ = original_import
        scorer = metrics.AdvancedMetrics('offline-encoder')
        assert not calls
        asyncio.run(scorer.initialize())
        asyncio.run(scorer.initialize())
        assert calls == ['offline-encoder']
        assert asyncio.run(scorer.score_coherence('First sentence. Second sentence.')) > 99
        """)


def test_missing_sentence_model_library_raises_actionable_error_on_first_use() -> None:
    _run("""
        import asyncio
        metrics = importlib.import_module('llm.evaluation_metrics')
        try:
            asyncio.run(metrics.AdvancedMetrics().initialize())
        except RuntimeError as exc:
            assert 'pip install sentence-transformers' in str(exc), str(exc)
        else:
            raise AssertionError('Missing model library was silently accepted')
        """)


def test_clip_first_use_and_cache_use_offline_model_factories() -> None:
    _run("""
        import types
        from contextlib import nullcontext
        import numpy as np
        from PIL import Image
        comparison = importlib.import_module('imagery.visual_comparison')
        calls = []
        class Features(np.ndarray):
            def norm(self, dim, keepdim):
                return np.linalg.norm(self, axis=dim, keepdims=keepdim)
        class OfflineModel:
            @classmethod
            def from_pretrained(cls, name):
                calls.append(('model', name))
                return cls()
            def eval(self):
                pass
            def get_image_features(self, **inputs):
                return np.array([[1., 0.], [1., 0.]]).view(Features)
        class OfflineProcessor:
            @classmethod
            def from_pretrained(cls, name):
                calls.append(('processor', name))
                return cls()
            def __call__(self, **kwargs):
                return {'pixel_values': None}
        sys.modules['torch'] = types.SimpleNamespace(no_grad=nullcontext)
        sys.modules['transformers'] = types.SimpleNamespace(CLIPModel=OfflineModel, CLIPProcessor=OfflineProcessor)
        builtins.__import__ = original_import
        comparison.CLIP_AVAILABLE = True
        engine = comparison.VisualComparisonEngine()
        assert not calls
        image = Image.new('RGB', (4, 4))
        assert engine.compute_clip_score(image, image) == 1.0
        assert engine.compute_clip_score(image, image) == 1.0
        assert [kind for kind, _ in calls] == ['model', 'processor']
        """)


@pytest.mark.parametrize("error", ["ImportError", "ModuleNotFoundError", "ValueError"])
def test_availability_probe_handles_failing_finders(error: str) -> None:
    _run(f"""
        from unittest.mock import patch
        comparison = importlib.import_module('imagery.visual_comparison')
        with patch.object(comparison.importlib.util, 'find_spec', side_effect={error}('blocked')):
            assert comparison._module_available('torch') is False
        """)
