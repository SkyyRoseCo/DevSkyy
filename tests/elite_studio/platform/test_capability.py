from unittest.mock import patch

import pytest

from skyyrose.elite_studio.platform.capability import CapabilityMatrix, CapabilityStatus
from skyyrose.elite_studio.platform.tenancy import TenantRegistry


def test_capability_status_is_immutable():
    s = CapabilityStatus(name="engine", ok=True, detail="ready")
    assert s.ok and s.name == "engine"


@pytest.mark.parametrize("engine_ready", [True, False])
def test_probe_returns_all_capabilities_without_spend(engine_ready):
    tenant = TenantRegistry.default().get("skyyrose")
    with patch(
        "agents.trellis_agent.TrellisAgent.is_available", return_value=engine_ready
    ) as probe:
        matrix = CapabilityMatrix(tenant).probe()
    probe.assert_called_once_with()
    names = {c.name for c in matrix.statuses}
    assert {"catalog", "reference_store", "fidelity_scorer", "engine_local"} <= names
    engine = next(c for c in matrix.statuses if c.name == "engine_local")
    assert engine.ok is engine_ready
    assert engine.detail == ("ready" if engine_ready else "env not ready")


def test_required_ok_false_when_a_required_cap_red():
    statuses = (
        CapabilityStatus(name="catalog", ok=False, detail="missing"),
        CapabilityStatus(name="engine_local", ok=True, detail="ready"),
    )
    matrix = CapabilityMatrix.__new__(CapabilityMatrix)
    object.__setattr__(matrix, "statuses", statuses)
    assert matrix.required_ok(required=("catalog",)) is False


def test_required_ok_true_when_all_required_green():
    statuses = (CapabilityStatus(name="catalog", ok=True, detail="ok"),)
    matrix = CapabilityMatrix.__new__(CapabilityMatrix)
    object.__setattr__(matrix, "statuses", statuses)
    assert matrix.required_ok(required=("catalog",)) is True
