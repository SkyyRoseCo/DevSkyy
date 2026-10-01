"""Legacy creative entrypoints deny before graph/provider import or paid work."""

import asyncio
import builtins

import pytest

from skyyrose.elite_studio.creative import nodes, runner
from skyyrose.elite_studio.creative.state import CreativeIntent

BLOCKED_NODES = [
    "entry_node",
    "product_render_node",
    "three_d_model_node",
    "social_pack_node",
    "character_node",
    "scene_composite_node",
    "design_ideation_node",
    "collection_plan_node",
    "tripo_generate_node",
]


@pytest.fixture
def no_provider_imports(monkeypatch):
    original = builtins.__import__
    attempted = []

    def guarded(name, *args, **kwargs):
        if any(
            word in name
            for word in (
                "router",
                "checkpointer",
                "_observability",
                "agents",
                "ai_3d",
                "fashion",
                "character",
                "openai",
                "anthropic",
                "fal_client",
                "replicate",
                "httpx",
                "requests",
            )
        ):
            attempted.append(name)
            raise AssertionError("Unexpected provider or graph import")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded)
    return attempted


@pytest.mark.parametrize("name", BLOCKED_NODES)
def test_direct_nodes_deny_untrusted_authority_before_import(name, no_provider_imports):
    result = getattr(nodes, name)(
        {
            "operation_id": "test",
            "intent": "product-render",
            "sku": "synthetic",
            "approved": True,
            "governor_context": {"authorized": True},
            "params": {
                "use_sdk_agent": True,
                "image_path": "/never-read",
                "spend_authorized": True,
            },
        }
    )
    assert result["error_code"] == "PAID_GOVERNOR_REQUIRED"
    assert result["paid_action_status"] == "UNSUPPORTED"
    assert result["provider_called"] is False
    assert result["status"] == "error"
    assert nodes.finalize_node(result) == {}
    assert not no_provider_imports


@pytest.mark.parametrize("intent", list(CreativeIntent))
def test_sync_entrypoint_cannot_reach_legacy_graph(intent, no_provider_imports):
    result = runner.run_creative(intent, {"approved": True})
    assert result["paid_action_status"] == "UNSUPPORTED"
    assert result["operation_id"]
    assert not no_provider_imports


def test_async_and_resume_deny_before_checkpoint_or_observability(no_provider_imports):
    first = asyncio.run(runner.arun_creative("product-render", {"authorized": True}))
    resumed = asyncio.run(runner.resume_creative("old-paid-checkpoint"))
    assert first["provider_called"] is False
    assert resumed["resumable"] is False
    assert resumed["operation_id"] == "old-paid-checkpoint"
    assert not no_provider_imports
