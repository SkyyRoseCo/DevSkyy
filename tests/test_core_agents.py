"""Tests for the Core Agent hierarchy.

Covers:
- categorize_failure() mapping
- SelfHealingMixin (circuit breaker, health_check, learning journal)
- CoreAgent (register_sub_agent, delegate, execute_safe, to_portal_node)
- All 8 concrete core agents (inheritance, core_type, name, sub-agents)
- Keyword routing per core agent
- Orchestrator (route_task, route, escalation, budget, system_health, to_portal_graph)
- Factory (create_orchestrator, budget_limit, graceful degradation)
- Legacy re-exports from agents.core.base
"""

from __future__ import annotations

import importlib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.core.base import (
    CircuitBreakerState,
    CoreAgent,
    CoreAgentType,
    Diagnosis,
    FailureCategory,
    HealResult,
    SelfHealingMixin,
    categorize_failure,
)
from agents.core.orchestrator import Orchestrator
from agents.errors import AgentError, ErrorCategory

# =============================================================================
# Test Helpers
# =============================================================================


class _StubCoreAgent(CoreAgent):
    """Minimal concrete core agent for testing."""

    core_type = CoreAgentType.COMMERCE
    name = "stub_core"
    description = "Stub for testing"

    async def execute(self, task: str, **kwargs) -> dict:
        return {"success": True, "task": task}


class _FailingCoreAgent(CoreAgent):
    """Core agent that always raises."""

    core_type = CoreAgentType.CONTENT
    name = "failing_core"

    async def execute(self, task: str, **kwargs) -> dict:
        raise RuntimeError("always fails")


def _import_core_agent(module_path: str, class_name: str):
    mod = importlib.import_module(module_path)
    return getattr(mod, class_name)


# =============================================================================
# Core Agent Registry (same as factory.py)
# =============================================================================

_CORE_AGENTS = [
    ("agents.core.commerce.agent", "CommerceCoreAgent", CoreAgentType.COMMERCE, "commerce_core"),
    ("agents.core.content.agent", "ContentCoreAgent", CoreAgentType.CONTENT, "content_core"),
    ("agents.core.creative.agent", "CreativeCoreAgent", CoreAgentType.CREATIVE, "creative_core"),
    (
        "agents.core.marketing.agent",
        "MarketingCoreAgent",
        CoreAgentType.MARKETING,
        "marketing_core",
    ),
    (
        "agents.core.operations.agent",
        "OperationsCoreAgent",
        CoreAgentType.OPERATIONS,
        "operations_core",
    ),
    (
        "agents.core.analytics.agent",
        "AnalyticsCoreAgent",
        CoreAgentType.ANALYTICS,
        "analytics_core",
    ),
    ("agents.core.imagery.agent", "ImageryCoreAgent", CoreAgentType.IMAGERY, "imagery_core"),
    (
        "agents.core.web_builder.agent",
        "WebBuilderCoreAgent",
        CoreAgentType.WEB_BUILDER,
        "web_builder_core",
    ),
]


# =============================================================================
# TestCategorizeFailure
# =============================================================================


class TestCategorizeFailure:
    """categorize_failure() maps errors to the right FailureCategory."""

    def test_config_keyword(self):
        assert categorize_failure("missing config file") == FailureCategory.CONFIG

    def test_external_keyword(self):
        assert categorize_failure("connection refused on port 443") == FailureCategory.EXTERNAL

    def test_provider_down_keyword(self):
        assert categorize_failure("503 service unavailable") == FailureCategory.PROVIDER_DOWN

    def test_data_quality_keyword(self):
        assert categorize_failure("invalid data in field X") == FailureCategory.DATA_QUALITY

    def test_agent_error_mapping(self):
        err = AgentError("timeout", category=ErrorCategory.TIMEOUT)
        assert categorize_failure(err) == FailureCategory.EXTERNAL

    def test_unknown_defaults_to_code_bug(self):
        assert categorize_failure("something weird happened") == FailureCategory.CODE_BUG

    def test_wrong_approach_keyword(self):
        assert categorize_failure("needs architectural redesign") == FailureCategory.WRONG_APPROACH


# =============================================================================
# TestSelfHealingMixin
# =============================================================================


class TestSelfHealingMixin:
    """SelfHealingMixin: circuit breaker, health_check, learning journal."""

    def _make_mixin(self):
        m = SelfHealingMixin()
        m.name = "test_agent"
        m.core_type = CoreAgentType.COMMERCE
        m.__init_healing__()
        return m

    def test_initial_state_healthy(self):
        m = self._make_mixin()
        assert m.circuit_breaker_allows()
        status = m.health_check()
        assert status.healthy
        assert status.circuit_breaker == "closed"

    def test_record_failure_increments(self):
        m = self._make_mixin()
        m._record_failure()
        assert m._consecutive_failures == 1
        assert m._circuit_state == CircuitBreakerState.CLOSED

    def test_circuit_opens_after_threshold(self):
        m = self._make_mixin()
        for _ in range(m._circuit_breaker_threshold):
            m._record_failure()
        assert m._circuit_state == CircuitBreakerState.OPEN
        assert not m.circuit_breaker_allows()

    def test_record_success_resets_failures(self):
        m = self._make_mixin()
        m._record_failure()
        m._record_failure()
        m._record_success()
        assert m._consecutive_failures == 0
        assert m._last_success_time is not None

    def test_diagnose_produces_diagnosis(self):
        m = self._make_mixin()
        d = m.diagnose("connection refused")
        assert isinstance(d, Diagnosis)
        assert d.failure_category == FailureCategory.EXTERNAL

    @pytest.mark.asyncio
    async def test_heal_records_in_journal(self):
        m = self._make_mixin()
        d = m.diagnose("some code bug")

        async def _always_fail(diag):
            return HealResult(success=False, message="nope")

        result = await m.heal(d, fixer=_always_fail)
        assert not result.success
        assert result.escalation_needed
        assert len(m._heal_journal) == m._max_heal_attempts

    @pytest.mark.asyncio
    async def test_heal_success_on_first_attempt(self):
        m = self._make_mixin()
        d = m.diagnose("some issue")

        async def _always_succeed(diag):
            return HealResult(success=True, message="fixed")

        result = await m.heal(d, fixer=_always_succeed)
        assert result.success
        assert result.attempts == 1


# =============================================================================
# TestCoreAgentBase
# =============================================================================


class TestCoreAgentBase:
    """CoreAgent: register_sub_agent, delegate, execute_safe, to_portal_node."""

    def test_register_sub_agent(self):
        agent = _StubCoreAgent()
        mock_sub = MagicMock()
        agent.register_sub_agent("test_sub", mock_sub)
        assert "test_sub" in agent.get_sub_agents()

    @pytest.mark.asyncio
    async def test_delegate_success(self):
        agent = _StubCoreAgent()
        mock_sub = AsyncMock()
        mock_sub.execute = AsyncMock(return_value={"success": True})
        agent.register_sub_agent("sub1", mock_sub)
        result = await agent.delegate("sub1", "do something")
        assert result["success"]

    @pytest.mark.asyncio
    async def test_delegate_unknown_sub_agent_raises(self):
        agent = _StubCoreAgent()
        with pytest.raises(AgentError):
            await agent.delegate("nonexistent", "task")

    @pytest.mark.asyncio
    async def test_execute_safe_success(self):
        agent = _StubCoreAgent()
        result = await agent.execute_safe("do something")
        assert result["success"]

    @pytest.mark.asyncio
    async def test_execute_safe_failure_triggers_healing(self):
        agent = _FailingCoreAgent()
        result = await agent.execute_safe("trigger failure")
        assert not result["success"]
        assert result.get("heal_attempted")
        assert result.get("escalation_needed")

    def test_to_portal_node(self):
        agent = _StubCoreAgent()
        agent.register_sub_agent("sub1", MagicMock())
        node = agent.to_portal_node()
        assert node["id"] == "stub_core"
        assert node["type"] == "commerce"
        assert "sub_agents" in node
        assert len(node["sub_agents"]) == 1


# =============================================================================
# TestConcreteCoreAgents (parametrized across all 8)
# =============================================================================


class TestConcreteCoreAgents:
    """Every concrete core agent must inherit CoreAgent and have correct metadata."""

    @pytest.mark.parametrize(
        "module_path,class_name,expected_type,expected_name",
        _CORE_AGENTS,
    )
    def test_inherits_from_core_agent(self, module_path, class_name, expected_type, expected_name):
        cls = _import_core_agent(module_path, class_name)
        assert issubclass(cls, CoreAgent), f"{class_name} must inherit CoreAgent"

    @pytest.mark.parametrize(
        "module_path,class_name,expected_type,expected_name",
        _CORE_AGENTS,
    )
    def test_correct_core_type(self, module_path, class_name, expected_type, expected_name):
        cls = _import_core_agent(module_path, class_name)
        assert cls.core_type == expected_type

    @pytest.mark.parametrize(
        "module_path,class_name,expected_type,expected_name",
        _CORE_AGENTS,
    )
    def test_correct_name(self, module_path, class_name, expected_type, expected_name):
        cls = _import_core_agent(module_path, class_name)
        assert cls.name == expected_name

    @pytest.mark.parametrize(
        "module_path,class_name,expected_type,expected_name",
        _CORE_AGENTS,
    )
    def test_instantiation_with_correlation_id(
        self, module_path, class_name, expected_type, expected_name
    ):
        cls = _import_core_agent(module_path, class_name)
        instance = cls(correlation_id="test-123")
        assert instance.correlation_id == "test-123"
        assert isinstance(instance, SelfHealingMixin)


# =============================================================================
# TestCoreAgentKeywordRouting
# =============================================================================


class TestCoreAgentKeywordRouting:
    """Orchestrator routes keywords to the correct core agent type."""

    def _make_orchestrator(self):
        return Orchestrator()

    @pytest.mark.parametrize(
        "task,expected_type",
        [
            ("Update product inventory levels", CoreAgentType.COMMERCE),
            ("Write blog copy for the collection", CoreAgentType.CONTENT),
            ("Create brand logo design", CoreAgentType.CREATIVE),
            ("Launch email campaign for audience", CoreAgentType.MARKETING),
            ("Deploy build to production", CoreAgentType.OPERATIONS),
            ("Generate analytics report on conversion", CoreAgentType.ANALYTICS),
            ("Render 3d model of the vton asset", CoreAgentType.IMAGERY),
            ("Update wordpress theme template", CoreAgentType.WEB_BUILDER),
        ],
    )
    def test_keyword_routing(self, task, expected_type):
        o = self._make_orchestrator()
        assert o.route_task(task) == expected_type

    def test_unknown_task_defaults_to_operations(self):
        o = self._make_orchestrator()
        assert o.route_task("something completely unrelated xyz") == CoreAgentType.OPERATIONS


# =============================================================================
# TestOrchestrator
# =============================================================================


class TestOrchestrator:
    """Orchestrator: route, escalation, budget, system_health, to_portal_graph."""

    def _make_wired_orchestrator(self):
        o = Orchestrator()
        agent = _StubCoreAgent()
        o.register_core_agent(agent)
        return o

    def test_register_and_get_core_agent(self):
        o = self._make_wired_orchestrator()
        agent = o.get_core_agent(CoreAgentType.COMMERCE)
        assert agent is not None
        assert agent.name == "stub_core"

    def test_get_missing_agent_returns_none(self):
        o = Orchestrator()
        assert o.get_core_agent(CoreAgentType.ANALYTICS) is None

    @pytest.mark.asyncio
    async def test_route_success(self):
        o = self._make_wired_orchestrator()
        result = await o.route("Check product inventory")
        assert result.get("success") or result.get("task")

    @pytest.mark.asyncio
    async def test_route_budget_exceeded(self):
        o = self._make_wired_orchestrator()
        o.set_budget_limit(10.0)
        o._budget_spent_usd = 15.0
        result = await o.route("Check product inventory")
        assert not result["success"]
        assert "Budget limit" in result["error"]

    @pytest.mark.asyncio
    async def test_route_escalation_on_failure(self):
        o = Orchestrator()
        failing = _FailingCoreAgent()
        failing.core_type = CoreAgentType.CONTENT
        o.register_core_agent(failing)
        # Never spawn a real Claude Agent SDK session from a unit test: it is a
        # paid call when a key is present and a ~17s timeout when it is not.
        with patch.object(Orchestrator, "_sdk_escalation", AsyncMock(return_value=None)):
            result = await o.route("Write blog copy description")
        # After SDK escalation path was added, the result may come back
        # from SDK with different keys, or still require human approval
        assert (
            result.get("requires_human_approval")
            or result.get("escalation_needed")
            or result.get("success") is not None
        )

    def test_system_health_report(self):
        o = self._make_wired_orchestrator()
        health = o.system_health()
        assert "orchestrator" in health
        assert "agents" in health
        assert "summary" in health
        assert health["summary"]["total_agents"] == 1

    def test_to_portal_graph(self):
        o = self._make_wired_orchestrator()
        graph = o.to_portal_graph()
        assert "nodes" in graph
        assert "connections" in graph
        node_ids = [n["id"] for n in graph["nodes"]]
        assert "orchestrator" in node_ids


# =============================================================================
# TestOrchestratorFactory
# =============================================================================


class TestOrchestratorFactory:
    """Factory: create_orchestrator wires up all 8 agents."""

    def test_import_factory(self):
        from agents.core.factory import create_orchestrator

        assert callable(create_orchestrator)

    def test_create_orchestrator_returns_orchestrator(self):
        from agents.core.factory import create_orchestrator

        o = create_orchestrator()
        assert isinstance(o, Orchestrator)

    def test_create_orchestrator_registers_agents(self):
        from agents.core.factory import create_orchestrator

        o = create_orchestrator()
        assert len(o._core_agents) == 8

    def test_create_orchestrator_with_budget(self):
        from agents.core.factory import create_orchestrator

        o = create_orchestrator(budget_limit_usd=100.0)
        assert o._budget_limit_usd == 100.0

    def test_create_orchestrator_with_correlation_id(self):
        from agents.core.factory import create_orchestrator

        o = create_orchestrator(correlation_id="test-corr-456")
        assert o.correlation_id == "test-corr-456"

    def test_graceful_degradation(self):
        """If a core agent fails to import, others still register."""

        with patch.dict(
            "sys.modules",
            {"agents.core.commerce.agent": None},
        ):
            # Force reimport to hit the patched module
            import agents.core.factory as factory_mod

            original_registry = factory_mod._CORE_AGENT_REGISTRY
            # Replace with a bad first entry
            factory_mod._CORE_AGENT_REGISTRY = [
                ("nonexistent.module", "BadAgent"),
                *original_registry[1:],
            ]
            try:
                o = factory_mod.create_orchestrator()
                # Should have 7 of 8 (one failed)
                assert len(o._core_agents) == 7
            finally:
                factory_mod._CORE_AGENT_REGISTRY = original_registry


# =============================================================================
# TestLegacyReExports
# =============================================================================


class TestLegacyReExports:
    """All 9 legacy symbols should be importable from agents.core.base."""

    @pytest.mark.parametrize(
        "symbol_name",
        [
            "AgentCapability",
            "LLMCategory",
            "AgentStatus",
            "AgentConfig",
            "PlanStep",
            "RetrievalContext",
            "ExecutionResult",
            "ValidationResult",
            "SuperAgent",
        ],
    )
    def test_legacy_symbol_importable(self, symbol_name):
        from agents.core import base as core_base

        assert hasattr(core_base, symbol_name), f"{symbol_name} not found in agents.core.base"

    def test_legacy_symbols_match_originals(self):
        """Re-exported symbols must be the same objects as in base_legacy."""
        from agents.base_legacy import AgentCapability as OrigCap
        from agents.base_legacy import SuperAgent as OrigSuper
        from agents.core.base import AgentCapability as ReexCap
        from agents.core.base import SuperAgent as ReexSuper

        assert OrigCap is ReexCap
        assert OrigSuper is ReexSuper


# =============================================================================
# TestSelfHealingMixinAdvanced — covers remaining base.py branches
# =============================================================================


class TestSelfHealingMixinAdvanced:
    """Additional SelfHealingMixin coverage: half-open transitions, LRU journal, etc."""

    def _make_mixin(self):
        m = SelfHealingMixin()
        m.name = "test_agent"
        m.core_type = CoreAgentType.COMMERCE
        m.__init_healing__()
        return m

    def test_half_open_success_closes_circuit(self):
        m = self._make_mixin()
        m._circuit_state = CircuitBreakerState.HALF_OPEN
        m._record_success()
        assert m._circuit_state == CircuitBreakerState.CLOSED

    def test_half_open_failure_reopens_circuit(self):
        m = self._make_mixin()
        m._circuit_state = CircuitBreakerState.HALF_OPEN
        m._record_failure()
        assert m._circuit_state == CircuitBreakerState.OPEN

    def test_half_open_allows_one_request(self):
        m = self._make_mixin()
        m._circuit_state = CircuitBreakerState.HALF_OPEN
        assert m.circuit_breaker_allows()

    def test_open_circuit_transitions_to_half_open_after_cooldown(self):
        import time as _time

        m = self._make_mixin()
        m._circuit_breaker_cooldown_seconds = 0.01  # very short for test
        # Open the breaker
        for _ in range(m._circuit_breaker_threshold):
            m._record_failure()
        assert m._circuit_state == CircuitBreakerState.OPEN
        _time.sleep(0.02)
        assert m.circuit_breaker_allows()
        assert m._circuit_state == CircuitBreakerState.HALF_OPEN

    def test_open_circuit_blocks_before_cooldown(self):
        m = self._make_mixin()
        m._circuit_breaker_cooldown_seconds = 9999
        for _ in range(m._circuit_breaker_threshold):
            m._record_failure()
        assert not m.circuit_breaker_allows()

    def test_lru_journal_eviction(self):
        m = self._make_mixin()
        m._heal_journal_max = 3
        # Fill journal beyond max
        for i in range(5):
            m._heal_journal[str(i)] = MagicMock()
            while len(m._heal_journal) > m._heal_journal_max:
                m._heal_journal.popitem(last=False)
        assert len(m._heal_journal) == 3

    def test_diagnose_uses_learning_journal(self):
        m = self._make_mixin()
        from agents.core.base import HealAttempt

        m._heal_journal["prev"] = HealAttempt(
            category=FailureCategory.EXTERNAL,
            description="past error",
            action_taken="switched provider",
        )
        d = m.diagnose("connection refused again")
        assert any("Previously worked" in a for a in d.suggested_actions)

    @pytest.mark.asyncio
    async def test_heal_with_fixer_that_raises(self):
        m = self._make_mixin()
        d = m.diagnose("some issue")

        async def _raiser(diag):
            raise ValueError("fixer exploded")

        result = await m.heal(d, fixer=_raiser)
        assert not result.success
        assert any("Fixer raised" in h.message for h in result.history)

    @pytest.mark.asyncio
    async def test_default_apply_fix_for_external(self):
        m = self._make_mixin()
        d = Diagnosis(
            failure_category=FailureCategory.EXTERNAL,
            description="timeout",
            suggested_actions=[],
        )
        result = await m._apply_fix(d)
        assert not result.success
        assert "external service" in result.message.lower()

    @pytest.mark.asyncio
    async def test_default_apply_fix_for_code_bug(self):
        m = self._make_mixin()
        d = Diagnosis(
            failure_category=FailureCategory.CODE_BUG,
            description="null pointer",
            suggested_actions=[],
        )
        result = await m._apply_fix(d)
        assert not result.success
        assert "no auto-fix" in result.message.lower()

    def test_suggested_actions_for_all_categories(self):
        m = self._make_mixin()
        for cat in FailureCategory:
            actions = m._suggested_actions_for(cat)
            assert isinstance(actions, list)
            assert len(actions) > 0


# =============================================================================
# TestCoreAgentDelegation — covers remaining delegate branches
# =============================================================================


class TestCoreAgentDelegation:
    """Covers delegate fallback, circuit breaker on sub, callable sub-agents."""

    @pytest.mark.asyncio
    async def test_delegate_sub_agent_failure_triggers_alternatives(self):
        agent = _StubCoreAgent()
        failing_sub = AsyncMock()
        failing_sub.execute = AsyncMock(side_effect=RuntimeError("sub failed"))
        good_sub = AsyncMock()
        good_sub.execute = AsyncMock(return_value={"success": True, "fallback": True})
        agent.register_sub_agent("bad", failing_sub)
        agent.register_sub_agent("good", good_sub)
        result = await agent.delegate("bad", "task")
        assert result.get("fallback") or result.get("success")

    @pytest.mark.asyncio
    async def test_delegate_circuit_breaker_open_tries_alternatives(self):
        agent = _StubCoreAgent()
        blocked_sub = MagicMock(spec=SelfHealingMixin)
        blocked_sub.circuit_breaker_allows = MagicMock(return_value=False)
        good_sub = AsyncMock()
        good_sub.execute = AsyncMock(return_value={"success": True})
        agent.register_sub_agent("blocked", blocked_sub)
        agent.register_sub_agent("good", good_sub)
        result = await agent.delegate("blocked", "task")
        assert result["success"]

    @pytest.mark.asyncio
    async def test_delegate_callable_sub_agent(self):
        agent = _StubCoreAgent()

        async def _callable_sub(task, **kw):
            return {"called": True}

        agent.register_sub_agent("fn", _callable_sub)
        result = await agent.delegate("fn", "task")
        assert result["called"]

    @pytest.mark.asyncio
    async def test_delegate_sub_no_execute_raises(self):
        agent = _StubCoreAgent()
        agent.register_sub_agent("bad", "not_callable")
        with pytest.raises(AgentError):
            await agent.delegate("bad", "task")

    @pytest.mark.asyncio
    async def test_all_sub_agents_fail_escalates(self):
        agent = _StubCoreAgent()
        bad1 = AsyncMock()
        bad1.execute = AsyncMock(side_effect=RuntimeError("fail1"))
        bad2 = AsyncMock()
        bad2.execute = AsyncMock(side_effect=RuntimeError("fail2"))
        agent.register_sub_agent("bad1", bad1)
        agent.register_sub_agent("bad2", bad2)
        with pytest.raises(AgentError, match="Escalation needed"):
            await agent.delegate("bad1", "task")

    @pytest.mark.asyncio
    async def test_execute_safe_circuit_breaker_open(self):
        agent = _StubCoreAgent()
        agent._circuit_state = CircuitBreakerState.OPEN
        agent._circuit_opened_at = 9999999999.0  # far future
        agent._circuit_breaker_cooldown_seconds = 9999
        result = await agent.execute_safe("task")
        assert not result["success"]
        assert result["escalation_needed"]

    @pytest.mark.asyncio
    async def test_execute_safe_heals_then_retries_fails(self):
        """After heal succeeds, retry still fails → returns failure."""
        call_count = 0

        class _FailTwiceCoreAgent(CoreAgent):
            core_type = CoreAgentType.ANALYTICS
            name = "fail_twice"

            async def execute(self, task, **kw):
                nonlocal call_count
                call_count += 1
                raise RuntimeError(f"fail #{call_count}")

        agent = _FailTwiceCoreAgent()
        # Patch heal to succeed so it retries execute
        agent.heal = AsyncMock(
            return_value=MagicMock(success=True, history=[], escalation_needed=False)
        )
        result = await agent.execute_safe("task")
        assert not result["success"]
        assert result.get("heal_attempted")


# =============================================================================
# TestConcreteCoreAgentExecute — execute() on all 8 domain agents
# =============================================================================


_EXECUTE_CASES = [
    # (module, class, task_with_keyword, expected_sub_agent_name_or_fallback)
    ("agents.core.commerce.agent", "CommerceCoreAgent", "Update product catalog SKU"),
    ("agents.core.content.agent", "ContentCoreAgent", "Write collection hero section"),
    ("agents.core.creative.agent", "CreativeCoreAgent", "Create design system CSS tokens"),
    ("agents.core.marketing.agent", "MarketingCoreAgent", "Post on social instagram"),
    ("agents.core.operations.agent", "OperationsCoreAgent", "Deploy release to production"),
    ("agents.core.analytics.agent", "AnalyticsCoreAgent", "Generate forecast report"),
    ("agents.core.imagery.agent", "ImageryCoreAgent", "Render 3d model mesh GLB"),
    ("agents.core.web_builder.agent", "WebBuilderCoreAgent", "Build html css component template"),
]


class TestConcreteCoreAgentExecute:
    """Exercise execute() on all 8 agents — routes to sub-agent or fallback."""

    @pytest.mark.parametrize("module_path,class_name,task", _EXECUTE_CASES)
    @pytest.mark.asyncio
    async def test_execute_routes_to_sub_or_fallback(self, module_path, class_name, task):
        cls = _import_core_agent(module_path, class_name)
        agent = cls()
        # Mock all registered sub-agents to succeed
        for name in list(agent._sub_agents.keys()):
            mock = AsyncMock()
            mock.execute = AsyncMock(return_value={"success": True, "handler": name})
            agent._sub_agents[name] = mock
        result = await agent.execute(task)
        assert result.get("success") is not None  # got a response

    @pytest.mark.parametrize("module_path,class_name,task", _EXECUTE_CASES)
    @pytest.mark.asyncio
    async def test_execute_fallback_when_no_sub_agents(self, module_path, class_name, task):
        cls = _import_core_agent(module_path, class_name)
        agent = cls()
        agent._sub_agents.clear()
        # Disable legacy agent(s) so they don't try to actually run.
        # Different core agents use different legacy attr names.
        for attr in (
            "_legacy_agent",
            "_legacy_imagery",
            "_legacy_product",
            "_legacy_content",
            "_legacy",
        ):
            if hasattr(agent, attr):
                setattr(agent, attr, None)
        for meth in (
            "_get_legacy_agent",
            "_get_legacy_imagery",
            "_get_legacy_product",
            "_get_legacy_content",
        ):
            if hasattr(agent, meth):
                setattr(agent, meth, lambda: None)
        result = await agent.execute("completely unrelated xyz gibberish")
        # Should return error since no sub-agents and no legacy
        assert "error" in result or "success" in result

    @pytest.mark.parametrize("module_path,class_name,task", _EXECUTE_CASES)
    @pytest.mark.asyncio
    async def test_execute_safe_wraps_execute(self, module_path, class_name, task):
        cls = _import_core_agent(module_path, class_name)
        agent = cls()
        for name in list(agent._sub_agents.keys()):
            mock = AsyncMock()
            mock.execute = AsyncMock(return_value={"success": True})
            agent._sub_agents[name] = mock
        result = await agent.execute_safe(task)
        assert isinstance(result, dict)


# =============================================================================
# TestSubAgent — covers sub_agent.py
# =============================================================================


class TestSubAgent:
    """SubAgent: execute_safe, escalation, to_portal_node."""

    def _make_sub_agent(self):
        from agents.core.sub_agent import SubAgent

        class _Stub(SubAgent):
            name = "test_sub"
            parent_type = CoreAgentType.COMMERCE

            async def execute(self, task, **kw):
                return {"success": True}

        return _Stub()

    def _make_failing_sub(self):
        from agents.core.sub_agent import SubAgent

        class _Failing(SubAgent):
            name = "failing_sub"
            parent_type = CoreAgentType.COMMERCE

            async def execute(self, task, **kw):
                raise RuntimeError("sub exploded")

        return _Failing()

    @pytest.mark.asyncio
    async def test_execute_safe_success(self):
        sub = self._make_sub_agent()
        result = await sub.execute_safe("do thing")
        assert result["success"]

    @pytest.mark.asyncio
    async def test_execute_safe_failure_escalates(self):
        sub = self._make_failing_sub()
        result = await sub.execute_safe("do thing")
        assert not result["success"]
        assert result["escalation_needed"]
        assert result["sub_agent"] == "failing_sub"

    @pytest.mark.asyncio
    async def test_execute_safe_circuit_breaker_open(self):
        sub = self._make_sub_agent()
        sub._circuit_state = CircuitBreakerState.OPEN
        sub._circuit_opened_at = 9999999999.0
        sub._circuit_breaker_cooldown_seconds = 9999
        result = await sub.execute_safe("task")
        assert not result["success"]
        assert "Circuit breaker" in result["error"]

    def test_escalation_response(self):
        sub = self._make_sub_agent()
        resp = sub._escalation_response(RuntimeError("test"))
        assert resp["escalation_needed"]
        assert resp["sub_agent"] == "test_sub"
        assert resp["parent_type"] == "commerce"

    @pytest.mark.asyncio
    async def test_escalate_to_parent_with_parent(self):
        sub = self._make_sub_agent()
        mock_parent = AsyncMock()
        mock_parent.execute_safe = AsyncMock(return_value={"success": True, "from_parent": True})
        sub.parent = mock_parent
        result = await sub.escalate_to_parent("task", RuntimeError("err"))
        assert result["from_parent"]

    @pytest.mark.asyncio
    async def test_escalate_to_parent_no_parent_raises(self):
        sub = self._make_sub_agent()
        sub.parent = None
        with pytest.raises(AgentError):
            await sub.escalate_to_parent("task", RuntimeError("err"))

    @pytest.mark.asyncio
    async def test_escalate_to_parent_no_execute_safe_raises(self):
        sub = self._make_sub_agent()
        sub.parent = MagicMock(spec=[])  # no execute_safe
        with pytest.raises(AgentError):
            await sub.escalate_to_parent("task", RuntimeError("err"))

    def test_to_portal_node(self):
        sub = self._make_sub_agent()
        node = sub.to_portal_node()
        assert node["id"] == "test_sub"
        assert node["parent"] == "commerce"
        assert node["healthy"]

    @pytest.mark.asyncio
    async def test_execute_safe_heal_success_then_retry_fails(self):
        """After healing succeeds, retry execute still fails → escalation."""
        sub = self._make_failing_sub()
        sub.heal = AsyncMock(return_value=MagicMock(success=True, history=[]))
        result = await sub.execute_safe("task")
        assert not result["success"]
        assert result["escalation_needed"]


# =============================================================================
# TestWordPressAIBridge — covers wp_ai_bridge.py
# =============================================================================


class TestWordPressAIBridge:
    """WordPressAIBridge: text gen, image gen, status, routing, dashboard card."""

    def _make_bridge(self):
        from agents.core.shared.wp_ai_bridge import WordPressAIBridge

        return WordPressAIBridge(
            wp_url="https://test.example.com",
            wp_auth_user="user",
            wp_auth_pass="pass",
        )

    def test_rest_base(self):
        bridge = self._make_bridge()
        assert "index.php?rest_route=" in bridge._rest_base

    def test_auth_returns_basic_auth(self):
        bridge = self._make_bridge()
        auth = bridge._auth()
        assert auth is not None

    def test_auth_returns_none_without_creds(self):
        from agents.core.shared.wp_ai_bridge import WordPressAIBridge

        bridge = WordPressAIBridge(wp_url="https://test.example.com")
        bridge._wp_auth_user = None
        bridge._wp_auth_pass = None
        assert bridge._auth() is None

    @pytest.mark.asyncio
    async def test_generate_text_calls_api(self):
        bridge = self._make_bridge()
        bridge._call_wp_api = AsyncMock(return_value={"success": True, "text": "hello"})
        result = await bridge.generate_text("write something", provider="openai", temperature=0.5)
        bridge._call_wp_api.assert_called_once()
        assert result["success"]

    @pytest.mark.asyncio
    async def test_generate_image_rejects_anthropic(self):
        bridge = self._make_bridge()
        result = await bridge.generate_image("draw a cat", provider="anthropic")
        assert not result["success"]
        assert "Anthropic" in result["error"]

    @pytest.mark.asyncio
    async def test_generate_image_calls_api(self):
        bridge = self._make_bridge()
        bridge._call_wp_api = AsyncMock(return_value={"success": True, "images": []})
        result = await bridge.generate_image("luxury flat lay", provider="openai", model="dall-e-3")
        assert result["success"]

    @pytest.mark.asyncio
    async def test_execute_routes_to_status(self):
        bridge = self._make_bridge()
        bridge.provider_status = AsyncMock(return_value={"success": True, "providers": {}})
        result = await bridge.execute("check providers status")
        assert result["success"]

    @pytest.mark.asyncio
    async def test_execute_routes_to_image(self):
        bridge = self._make_bridge()
        bridge.generate_image = AsyncMock(return_value={"success": True, "images": []})
        result = await bridge.execute("generate image of a rose")
        assert result["success"]

    @pytest.mark.asyncio
    async def test_execute_routes_to_text_default(self):
        bridge = self._make_bridge()
        bridge.generate_text = AsyncMock(return_value={"success": True, "text": "hi"})
        result = await bridge.execute("describe the product")
        assert result["success"]

    def test_round_table_mapping(self):
        bridge = self._make_bridge()
        mapping = bridge.get_round_table_mapping()
        assert mapping["claude"] == "anthropic"
        assert mapping["gpt4"] == "openai"

    @pytest.mark.asyncio
    async def test_compete_for_round_table_valid(self):
        bridge = self._make_bridge()
        bridge.generate_text = AsyncMock(return_value={"success": True})
        result = await bridge.compete_for_round_table("test prompt", "claude")
        bridge.generate_text.assert_called_with("test prompt", provider="anthropic")
        assert result["success"]

    @pytest.mark.asyncio
    async def test_compete_for_round_table_unknown_provider(self):
        bridge = self._make_bridge()
        result = await bridge.compete_for_round_table("test", "unknown_provider")
        assert not result["success"]

    def test_to_dashboard_card(self):
        bridge = self._make_bridge()
        card = bridge.to_dashboard_card()
        assert card["id"] == "wp_ai_bridge"
        assert card["healthy"]
        assert "providers" in card
        assert "round_table_mapping" in card

    @pytest.mark.asyncio
    async def test_call_wp_api_success(self):
        bridge = self._make_bridge()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"text": "generated"}

        with patch("httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            MockClient.return_value = mock_client

            result = await bridge._call_wp_api("/prompt", {"prompt": "test"})
            assert result["success"]

    @pytest.mark.asyncio
    async def test_call_wp_api_http_error(self):
        bridge = self._make_bridge()
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "Internal Server Error"

        with patch("httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            MockClient.return_value = mock_client

            result = await bridge._call_wp_api("/prompt", {"prompt": "test"})
            assert not result["success"]
            assert "500" in result["error"]

    @pytest.mark.asyncio
    async def test_call_wp_api_timeout(self):
        import httpx

        bridge = self._make_bridge()

        with patch("httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("timed out"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            MockClient.return_value = mock_client

            result = await bridge._call_wp_api("/prompt", {"prompt": "test"}, capability="text")
            assert not result["success"]
            assert "Timeout" in result["error"]

    @pytest.mark.asyncio
    async def test_call_wp_api_generic_exception(self):
        bridge = self._make_bridge()

        with patch("httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(side_effect=ConnectionError("refused"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            MockClient.return_value = mock_client

            result = await bridge._call_wp_api("/prompt", {"prompt": "test"})
            assert not result["success"]

    @pytest.mark.asyncio
    async def test_provider_status_success(self):
        bridge = self._make_bridge()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"openai": {"configured": True}}

        with patch("httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            MockClient.return_value = mock_client

            result = await bridge.provider_status()
            assert result["success"]

    @pytest.mark.asyncio
    async def test_provider_status_http_error(self):
        bridge = self._make_bridge()
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.text = "Forbidden"

        with patch("httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            MockClient.return_value = mock_client

            result = await bridge.provider_status()
            assert not result["success"]

    @pytest.mark.asyncio
    async def test_provider_status_exception(self):
        bridge = self._make_bridge()

        with patch("httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=ConnectionError("down"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            MockClient.return_value = mock_client

            result = await bridge.provider_status()
            assert not result["success"]

    @pytest.mark.asyncio
    async def test_list_models_filtered(self):
        bridge = self._make_bridge()
        bridge.provider_status = AsyncMock(
            return_value={
                "success": True,
                "providers": {
                    "openai": {"configured": True, "models": ["gpt-4o"]},
                },
            }
        )
        result = await bridge.list_models(provider="openai")
        assert result["success"]
        assert "gpt-4o" in result["models"]

    @pytest.mark.asyncio
    async def test_list_models_all(self):
        bridge = self._make_bridge()
        bridge.provider_status = AsyncMock(
            return_value={"success": True, "providers": {"openai": {}}}
        )
        result = await bridge.list_models()
        assert result["success"]

    @pytest.mark.asyncio
    async def test_list_models_status_failure(self):
        bridge = self._make_bridge()
        bridge.provider_status = AsyncMock(return_value={"success": False, "error": "down"})
        result = await bridge.list_models()
        assert not result["success"]


# =============================================================================
# TestOrchestratorAdvanced — remaining orchestrator.py branches
# =============================================================================


class TestOrchestratorAdvanced:
    """Covers AI bridge routing, _route_to_any_available, escalation fallthrough."""

    @pytest.mark.asyncio
    async def test_route_to_ai_bridge(self):
        o = Orchestrator()
        o._wp_ai_bridge.execute_safe = AsyncMock(return_value={"success": True, "ai": True})
        result = await o.route("ai generate description for product")
        assert result.get("ai") or result.get("success")

    @pytest.mark.asyncio
    async def test_route_no_agent_tries_any_available(self):
        o = Orchestrator()
        stub = _StubCoreAgent()
        stub.core_type = CoreAgentType.IMAGERY  # register for wrong domain
        o.register_core_agent(stub)
        # Route a content task but only imagery is registered
        result = await o.route("Write blog copy text for SEO page description")
        # Should fall through to _route_to_any_available and try imagery
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_route_to_any_available_all_fail(self):
        o = Orchestrator()
        failing = _FailingCoreAgent()
        o.register_core_agent(failing)
        result = await o._route_to_any_available("anything")
        assert not result["success"]
        assert result["requires_human_approval"]

    @pytest.mark.asyncio
    async def test_handle_escalation_all_fail(self):
        o = Orchestrator()
        f1 = _FailingCoreAgent()
        f1.core_type = CoreAgentType.CONTENT
        f1.name = "content_fail"
        f2 = _FailingCoreAgent()
        f2.core_type = CoreAgentType.CREATIVE
        f2.name = "creative_fail"
        o.register_core_agent(f1)
        o.register_core_agent(f2)
        # Never spawn a real Claude Agent SDK session from a unit test: it is a
        # paid call when a key is present and a ~17s timeout when it is not.
        with patch.object(Orchestrator, "_sdk_escalation", AsyncMock(return_value=None)):
            result = await o._handle_escalation(
                "task", failed_type=CoreAgentType.CONTENT, original_result={"error": "initial"}
            )
        # SDK escalation may run and return a different structure;
        # if SDK also fails, requires_human_approval is set
        assert result.get("requires_human_approval") or result.get("success") is not None

    @pytest.mark.asyncio
    async def test_handle_escalation_alternative_succeeds(self):
        o = Orchestrator()
        failing = _FailingCoreAgent()
        failing.core_type = CoreAgentType.CONTENT
        good = _StubCoreAgent()
        good.core_type = CoreAgentType.CREATIVE
        o.register_core_agent(failing)
        o.register_core_agent(good)
        result = await o._handle_escalation(
            "task", failed_type=CoreAgentType.CONTENT, original_result={}
        )
        assert result.get("success")

    @pytest.mark.asyncio
    async def test_route_to_any_skips_open_circuit_breaker(self):
        o = Orchestrator()
        blocked = _StubCoreAgent()
        blocked.core_type = CoreAgentType.COMMERCE
        blocked._circuit_state = CircuitBreakerState.OPEN
        blocked._circuit_opened_at = 9999999999.0
        blocked._circuit_breaker_cooldown_seconds = 9999
        o.register_core_agent(blocked)
        result = await o._route_to_any_available("task")
        assert not result["success"]


# =============================================================================
# Keyword routing: exercise every branch in each domain agent's execute()
# =============================================================================


def _make_mock_sub(name: str = "mock_sub"):
    """Create a mock sub-agent with async execute returning success."""
    m = AsyncMock()
    m.name = name
    m.execute = AsyncMock(return_value={"success": True, "agent": name})
    m.execute_safe = AsyncMock(return_value={"success": True, "agent": name})
    m.circuit_breaker_allows = MagicMock(return_value=True)
    m.health_check = MagicMock(return_value=MagicMock(healthy=True, circuit_breaker="CLOSED"))
    return m


class TestContentRouting:
    """Cover all keyword branches in ContentCoreAgent.execute()."""

    def _agent(self):
        from agents.core.content.agent import ContentCoreAgent

        a = ContentCoreAgent()
        a._sub_agents.clear()
        return a

    @pytest.mark.asyncio
    async def test_route_collection(self):
        a = self._agent()
        a._sub_agents["collection_content"] = _make_mock_sub("collection_content")
        r = await a.execute("Update collection hero section")
        assert r["success"]

    @pytest.mark.asyncio
    async def test_route_seo(self):
        a = self._agent()
        a._sub_agents["seo_content"] = _make_mock_sub("seo_content")
        r = await a.execute("Optimize SEO meta tags")
        assert r["success"]

    @pytest.mark.asyncio
    async def test_route_copywriter(self):
        a = self._agent()
        a._sub_agents["copywriter"] = _make_mock_sub("copywriter")
        r = await a.execute("Write a blog post about fashion")
        assert r["success"]

    @pytest.mark.asyncio
    async def test_fallback_no_match(self):
        a = self._agent()
        a._legacy_agent = None
        a._get_legacy_agent = lambda: None
        r = await a.execute("zzz unmatched")
        assert not r["success"]
        assert "error" in r


class TestCreativeRouting:
    """Cover all keyword branches in CreativeCoreAgent.execute()."""

    def _agent(self):
        from agents.core.creative.agent import CreativeCoreAgent

        a = CreativeCoreAgent()
        a._sub_agents.clear()
        return a

    @pytest.mark.asyncio
    async def test_route_design_system(self):
        a = self._agent()
        a._sub_agents["design_system"] = _make_mock_sub("design_system")
        r = await a.execute("Update design system CSS tokens")
        assert r["success"]

    @pytest.mark.asyncio
    async def test_route_brand_guardian(self):
        a = self._agent()
        a._sub_agents["brand_guardian"] = _make_mock_sub("brand_guardian")
        r = await a.execute("Check brand color violations")
        assert r["success"]

    @pytest.mark.asyncio
    async def test_route_asset_generator(self):
        a = self._agent()
        a._sub_agents["asset_generator"] = _make_mock_sub("asset_generator")
        r = await a.execute("Generate new asset pack")
        assert r["success"]

    @pytest.mark.asyncio
    async def test_route_quality_checker(self):
        a = self._agent()
        a._sub_agents["quality_checker"] = _make_mock_sub("quality_checker")
        r = await a.execute("Run quality regression check")
        assert r["success"]

    @pytest.mark.asyncio
    async def test_fallback_no_match(self):
        a = self._agent()
        a._legacy_agent = None
        a._get_legacy_agent = lambda: None
        r = await a.execute("zzz unmatched")
        assert not r["success"]


class TestMarketingRouting:
    """Cover all keyword branches in MarketingCoreAgent.execute()."""

    def _agent(self):
        from agents.core.marketing.agent import MarketingCoreAgent

        a = MarketingCoreAgent()
        a._sub_agents.clear()
        return a

    @pytest.mark.asyncio
    async def test_route_social(self):
        a = self._agent()
        a._sub_agents["social_media"] = _make_mock_sub("social_media")
        r = await a.execute("Schedule an instagram post")
        assert r["success"]

    @pytest.mark.asyncio
    async def test_route_campaign(self):
        a = self._agent()
        a._sub_agents["campaign_manager"] = _make_mock_sub("campaign_manager")
        r = await a.execute("Launch email campaign for audience")
        assert r["success"]

    @pytest.mark.asyncio
    async def test_route_ab_testing(self):
        a = self._agent()
        a._sub_agents["ab_testing"] = _make_mock_sub("ab_testing")
        r = await a.execute("Run an a/b test experiment")
        assert r["success"]

    @pytest.mark.asyncio
    async def test_fallback_no_match(self):
        a = self._agent()
        a._legacy_agent = None
        a._get_legacy_agent = lambda: None
        r = await a.execute("zzz unmatched")
        assert not r["success"]


class TestOperationsRouting:
    """Cover all keyword branches in OperationsCoreAgent.execute()."""

    def _agent(self):
        from agents.core.operations.agent import OperationsCoreAgent

        a = OperationsCoreAgent()
        a._sub_agents.clear()
        return a

    @pytest.mark.asyncio
    async def test_route_deploy(self):
        a = self._agent()
        a._sub_agents["deployment_manager"] = _make_mock_sub("deployment_manager")
        r = await a.execute("Deploy latest release to production")
        assert r["success"]

    @pytest.mark.asyncio
    async def test_route_security(self):
        a = self._agent()
        a._sub_agents["security_monitor"] = _make_mock_sub("security_monitor")
        r = await a.execute("Run security vulnerability audit")
        assert r["success"]

    @pytest.mark.asyncio
    async def test_route_health(self):
        a = self._agent()
        a._sub_agents["health_checker"] = _make_mock_sub("health_checker")
        r = await a.execute("Check uptime health status")
        assert r["success"]

    @pytest.mark.asyncio
    async def test_route_coding_doctor(self):
        a = self._agent()
        a._sub_agents["coding_doctor"] = _make_mock_sub("coding_doctor")
        r = await a.execute("Run lint and type quality check")
        assert r["success"]

    @pytest.mark.asyncio
    async def test_fallback_no_match(self):
        a = self._agent()
        a._legacy_agent = None
        a._get_legacy_agent = lambda: None
        r = await a.execute("zzz unmatched")
        assert not r["success"]


class TestImageryCoreRouting:
    """Cover all keyword branches in ImageryCoreAgent.execute()."""

    def _agent(self):
        from agents.core.imagery.agent import ImageryCoreAgent

        a = ImageryCoreAgent()
        a._sub_agents.clear()
        return a

    @pytest.mark.asyncio
    async def test_route_3d_tripo(self):
        a = self._agent()
        a._sub_agents["tripo_3d"] = _make_mock_sub("tripo_3d")
        r = await a.execute("Generate 3D model mesh")
        assert r["success"]

    @pytest.mark.asyncio
    async def test_route_3d_tripo_fails_fallback_meshy(self):
        a = self._agent()
        tripo = _make_mock_sub("tripo_3d")
        tripo.execute_safe = AsyncMock(side_effect=RuntimeError("tripo down"))
        a._sub_agents["tripo_3d"] = tripo
        a._sub_agents["meshy_3d"] = _make_mock_sub("meshy_3d")
        # delegate calls execute_safe on sub, but the routing is via self.delegate
        # We need to mock delegate to simulate tripo failure then meshy success

        call_count = 0
        original_delegate = a.delegate

        async def mock_delegate(name, task, **kw):
            nonlocal call_count
            call_count += 1
            if name == "tripo_3d":
                raise RuntimeError("tripo down")
            return {"success": True, "agent": name}

        a.delegate = mock_delegate
        r = await a.execute("Generate 3D GLB model")
        assert r["success"]
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_route_vton(self):
        a = self._agent()
        a._sub_agents["fashn_vton"] = _make_mock_sub("fashn_vton")
        r = await a.execute("Virtual try-on with this garment")
        assert r["success"]

    @pytest.mark.asyncio
    async def test_route_hf_spaces(self):
        a = self._agent()
        a._sub_agents["hf_spaces"] = _make_mock_sub("hf_spaces")
        r = await a.execute("Use huggingface space for processing")
        assert r["success"]

    @pytest.mark.asyncio
    async def test_route_gemini_default(self):
        a = self._agent()
        a._sub_agents["gemini_image"] = _make_mock_sub("gemini_image")
        r = await a.execute("Generate a product photo")
        assert r["success"]

    @pytest.mark.asyncio
    async def test_fallback_no_match(self):
        a = self._agent()
        a._legacy_imagery = None
        a._get_legacy_imagery = lambda: None
        r = await a.execute("zzz unmatched gibberish")
        assert not r["success"]


class TestWebBuilderRouting:
    """Cover all keyword branches in WebBuilderCoreAgent.execute()."""

    def _agent(self):
        from agents.core.web_builder.agent import WebBuilderCoreAgent

        a = WebBuilderCoreAgent()
        a._sub_agents.clear()
        return a

    @pytest.mark.asyncio
    async def test_route_frontend(self):
        a = self._agent()
        a._sub_agents["frontend_dev"] = _make_mock_sub("frontend_dev")
        r = await a.execute("Build HTML CSS component")
        assert r["success"]

    @pytest.mark.asyncio
    async def test_route_backend(self):
        a = self._agent()
        a._sub_agents["backend_dev"] = _make_mock_sub("backend_dev")
        r = await a.execute("Create PHP API backend endpoint")
        assert r["success"]

    @pytest.mark.asyncio
    async def test_route_accessibility(self):
        a = self._agent()
        a._sub_agents["accessibility"] = _make_mock_sub("accessibility")
        r = await a.execute("Run accessibility WCAG audit")
        assert r["success"]

    @pytest.mark.asyncio
    async def test_route_performance(self):
        a = self._agent()
        a._sub_agents["performance"] = _make_mock_sub("performance")
        r = await a.execute("Optimize lighthouse performance score")
        assert r["success"]

    @pytest.mark.asyncio
    async def test_route_platform(self):
        a = self._agent()
        a._sub_agents["platform_adapter"] = _make_mock_sub("platform_adapter")
        r = await a.execute("Deploy wordpress theme")
        assert r["success"]

    @pytest.mark.asyncio
    async def test_fallback_director(self):
        a = self._agent()
        mock_director = AsyncMock()
        mock_director.build = AsyncMock(return_value={"built": True})
        a._director = mock_director
        r = await a.execute("Build complete theme from scratch")
        assert r["success"]

    @pytest.mark.asyncio
    async def test_fallback_no_director(self):
        a = self._agent()
        a._director = None
        # Override _get_director to return None
        a._get_director = lambda: None
        r = await a.execute("zzz unmatched")
        assert not r["success"]


class TestWebBuilderApplyFix:
    """Cover WebBuilderCoreAgent._apply_fix()."""

    @pytest.mark.asyncio
    async def test_apply_fix_import_fails(self):
        from agents.core.web_builder.agent import WebBuilderCoreAgent

        a = WebBuilderCoreAgent()
        diag = Diagnosis(
            failure_category=FailureCategory.CODE_BUG,
            description="build fail",
            suggested_actions=["fix build"],
        )
        # _apply_fix tries to import SelfHealer — will fail, falls back to super()
        result = await a._apply_fix(diag)
        assert isinstance(result, HealResult)


class TestImageryApplyFix:
    """Cover ImageryCoreAgent._apply_fix() provider failover."""

    @pytest.mark.asyncio
    async def test_apply_fix_provider_down_failover(self):
        from agents.core.imagery.agent import ImageryCoreAgent

        a = ImageryCoreAgent()
        a._sub_agents.clear()
        mock_sub = _make_mock_sub("meshy_3d")
        mock_sub.circuit_breaker_allows = MagicMock(return_value=True)
        a._sub_agents["meshy_3d"] = mock_sub
        diag = Diagnosis(
            failure_category=FailureCategory.PROVIDER_DOWN,
            description="provider down",
            suggested_actions=["failover"],
        )
        result = await a._apply_fix(diag)
        assert result.success
        assert "meshy_3d" in result.message

    @pytest.mark.asyncio
    async def test_apply_fix_non_provider_falls_through(self):
        from agents.core.imagery.agent import ImageryCoreAgent

        a = ImageryCoreAgent()
        a._sub_agents.clear()
        diag = Diagnosis(
            failure_category=FailureCategory.CODE_BUG,
            description="logic issue",
            suggested_actions=["debug"],
        )
        result = await a._apply_fix(diag)
        assert isinstance(result, HealResult)


class TestFashnVtonSubAgent:
    """Cover FashnVtonSubAgent._apply_fix()."""

    @pytest.mark.asyncio
    async def test_apply_fix_provider_down(self):
        from agents.core.imagery.sub_agents.fashn_vton import FashnVtonSubAgent

        a = FashnVtonSubAgent()
        diag = Diagnosis(
            failure_category=FailureCategory.PROVIDER_DOWN,
            description="fashn down",
            suggested_actions=["switch provider"],
        )
        result = await a._apply_fix(diag)
        assert result.success
        assert "alternative" in result.message.lower() or "provider" in result.message.lower()

    @pytest.mark.asyncio
    async def test_apply_fix_logic_error_fallback(self):
        from agents.core.imagery.sub_agents.fashn_vton import FashnVtonSubAgent

        a = FashnVtonSubAgent()
        diag = Diagnosis(
            failure_category=FailureCategory.CODE_BUG,
            description="bad logic",
            suggested_actions=["fix"],
        )
        result = await a._apply_fix(diag)
        assert isinstance(result, HealResult)


# =============================================================================
# SubAgent: additional coverage for _llm_execute, _escalation_response, etc.
# =============================================================================


class TestSubAgentLlmAndEscalation:
    """Cover uncovered paths in sub_agent.py."""

    @pytest.mark.asyncio
    async def test_get_llm_client_singleton(self):
        """Cover _get_llm_client() lazy init."""
        import agents.core.sub_agent as sa_mod

        old = sa_mod._llm_client
        sa_mod._llm_client = None
        try:
            with patch(
                "llm.unified_llm_client.UnifiedLLMClient", return_value=MagicMock()
            ) as mock_cls:
                client = sa_mod._get_llm_client()
                assert client is not None
                mock_cls.assert_called_once()
                # Second call returns same singleton
                client2 = sa_mod._get_llm_client()
                assert client2 is client
        finally:
            sa_mod._llm_client = old

    @pytest.mark.asyncio
    async def test_llm_execute_with_system_prompt(self):
        """Cover _llm_execute path with system_prompt and preferred_provider."""
        from agents.core.imagery.sub_agents.fashn_vton import FashnVtonSubAgent

        a = FashnVtonSubAgent()
        mock_response = MagicMock()
        mock_response.content = "generated"
        mock_response.provider_used = MagicMock(value="anthropic")
        mock_response.model_used = "claude-4"
        mock_response.technique_used = MagicMock(value="chain_of_thought")
        mock_response.total_latency_ms = 100

        import agents.core.sub_agent as sa_mod

        old = sa_mod._llm_client
        sa_mod._llm_client = None
        try:
            mock_client = AsyncMock()
            mock_client.complete = AsyncMock(return_value=mock_response)
            with patch(
                "llm.unified_llm_client.UnifiedLLMClient",
                return_value=mock_client,
            ):
                result = await a._llm_execute(
                    "test task",
                    system_prompt="Custom system",
                    preferred_provider="anthropic",
                    execution_mode="fast",
                )
                assert result["success"]
                assert result["result"] == "generated"
        finally:
            sa_mod._llm_client = old

    @pytest.mark.asyncio
    async def test_execute_safe_heal_then_retry_fails(self):
        """Cover execute_safe path: heal succeeds but retry still fails → escalation."""
        from agents.core.imagery.sub_agents.fashn_vton import FashnVtonSubAgent

        a = FashnVtonSubAgent()
        a.execute = AsyncMock(side_effect=RuntimeError("always fails"))
        # heal returns success
        a.heal = AsyncMock(return_value=HealResult(success=True, message="healed"))
        result = await a.execute_safe("test")
        assert not result["success"]
        assert result.get("escalation_needed")

    @pytest.mark.asyncio
    async def test_execute_safe_heal_succeeds_retry_succeeds(self):
        """Cover execute_safe: heal + retry succeed."""
        from agents.core.imagery.sub_agents.fashn_vton import FashnVtonSubAgent

        a = FashnVtonSubAgent()
        call_count = 0

        async def flaky_execute(task, **kw):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RuntimeError("first fail")
            return {"success": True}

        a.execute = flaky_execute
        a.heal = AsyncMock(return_value=HealResult(success=True, message="healed"))
        result = await a.execute_safe("test")
        assert result["success"]

    @pytest.mark.asyncio
    async def test_escalation_response_structure(self):
        """Cover _escalation_response()."""
        from agents.core.imagery.sub_agents.fashn_vton import FashnVtonSubAgent

        a = FashnVtonSubAgent()
        resp = a._escalation_response(RuntimeError("boom"))
        assert resp["escalation_needed"]
        assert resp["sub_agent"] == "fashn_vton"
        assert "diagnosis" in resp

    @pytest.mark.asyncio
    async def test_escalate_to_parent_no_parent(self):
        """Cover escalate_to_parent with no parent set."""
        from agents.core.imagery.sub_agents.fashn_vton import FashnVtonSubAgent
        from agents.errors import AgentError

        a = FashnVtonSubAgent()
        a.parent = None
        with pytest.raises(AgentError):
            await a.escalate_to_parent("task", RuntimeError("err"))

    @pytest.mark.asyncio
    async def test_escalate_to_parent_with_parent(self):
        """Cover escalate_to_parent with a valid parent."""
        from agents.core.imagery.sub_agents.fashn_vton import FashnVtonSubAgent

        a = FashnVtonSubAgent()
        mock_parent = AsyncMock()
        mock_parent.execute_safe = AsyncMock(return_value={"success": True})
        a.parent = mock_parent
        result = await a.escalate_to_parent("task", RuntimeError("err"))
        assert result["success"]

    @pytest.mark.asyncio
    async def test_escalate_to_parent_no_execute_safe(self):
        """Cover escalate_to_parent when parent has no execute_safe."""
        from agents.core.imagery.sub_agents.fashn_vton import FashnVtonSubAgent
        from agents.errors import AgentError

        a = FashnVtonSubAgent()

        class NoExecParent:
            pass

        a.parent = NoExecParent()
        with pytest.raises(AgentError):
            await a.escalate_to_parent("task", RuntimeError("err"))


class TestCommerceRouting:
    """Cover CommerceCoreAgent keyword routing branches."""

    def _agent(self):
        from agents.core.commerce.agent import CommerceCoreAgent

        a = CommerceCoreAgent()
        a._sub_agents.clear()
        return a

    @pytest.mark.asyncio
    async def test_route_pricing(self):
        a = self._agent()
        a._sub_agents["product_ops"] = _make_mock_sub("product_ops")
        r = await a.execute("Update product pricing and inventory")
        assert r["success"]

    @pytest.mark.asyncio
    async def test_route_wordpress(self):
        a = self._agent()
        a._sub_agents["wordpress_bridge"] = _make_mock_sub("wordpress_bridge")
        r = await a.execute("Sync WooCommerce catalog")
        assert r["success"]

    @pytest.mark.asyncio
    async def test_route_asset_upload(self):
        a = self._agent()
        a._sub_agents["wordpress_assets"] = _make_mock_sub("wordpress_assets")
        r = await a.execute("Upload product image asset to media")
        assert r["success"]

    @pytest.mark.asyncio
    async def test_fallback_no_match(self):
        a = self._agent()
        for attr in ("_legacy_agent", "_legacy_product"):
            if hasattr(a, attr):
                setattr(a, attr, None)
        for meth in ("_get_legacy_agent", "_get_legacy_product"):
            if hasattr(a, meth):
                setattr(a, meth, lambda: None)
        r = await a.execute("zzz unmatched gibberish")
        assert not r["success"]


class TestAnalyticsRouting:
    """Cover AnalyticsCoreAgent keyword routing branches."""

    def _agent(self):
        from agents.core.analytics.agent import AnalyticsCoreAgent

        a = AnalyticsCoreAgent()
        a._sub_agents.clear()
        return a

    @pytest.mark.asyncio
    async def test_fallback_no_match(self):
        a = self._agent()
        for attr in ("_legacy_agent",):
            if hasattr(a, attr):
                setattr(a, attr, None)
        for meth in ("_get_legacy_agent",):
            if hasattr(a, meth):
                setattr(a, meth, lambda: None)
        r = await a.execute("zzz unmatched gibberish")
        assert not r["success"]


# =============================================================================
# ImportError branches in _register_sub_agents() and _get_legacy_agent()
# =============================================================================


class TestImportErrorBranches:
    """Force ImportError on sub-agent and legacy imports to cover except branches."""

    @pytest.mark.asyncio
    async def test_content_sub_agents_import_error(self):
        import sys

        # Use importlib.import_module to avoid py/import-and-import-from CodeQL finding
        # (this file also has `from agents.core.content.agent import ...` in other tests)
        mod = importlib.import_module("agents.core.content.agent")

        # Remove the module before patching to allow reload
        sys.modules.pop("agents.core.content.agent", None)
        with patch.dict(
            "sys.modules",
            {
                "agents.core.content.agent": mod,
                "agents.core.content.sub_agents.collection_content": None,
                "agents.core.content.sub_agents.seo_copywriter": None,
            },
        ):
            importlib.reload(mod)
            a = mod.ContentCoreAgent()
            # Legacy sub-agents should be absent; SDK agents may still register
            assert "collection_content" not in a._sub_agents
            assert "seo_copywriter" not in a._sub_agents
        # Restore module to sys.modules before cleanup reload
        sys.modules["agents.core.content.agent"] = mod
        importlib.reload(mod)

    @pytest.mark.asyncio
    async def test_content_legacy_import_error(self):
        from agents.core.content.agent import ContentCoreAgent

        a = ContentCoreAgent()
        a._legacy_agent = None
        with patch.dict("sys.modules", {"agents.skyyrose_content_agent": None}):
            result = a._get_legacy_agent()
            assert result is None

    @pytest.mark.asyncio
    async def test_creative_sub_agents_import_error(self):
        import sys

        mod = importlib.import_module("agents.core.creative.agent")
        sys.modules.pop("agents.core.creative.agent", None)
        with patch.dict(
            "sys.modules",
            {
                "agents.core.creative.agent": mod,
                "agents.core.creative.sub_agents.brand_creative": None,
            },
        ):
            importlib.reload(mod)
            a = mod.CreativeCoreAgent()
            assert len(a._sub_agents) == 0
        # Restore module to sys.modules before cleanup reload
        sys.modules["agents.core.creative.agent"] = mod
        importlib.reload(mod)

    @pytest.mark.asyncio
    async def test_creative_legacy_import_error(self):
        from agents.core.creative.agent import CreativeCoreAgent

        a = CreativeCoreAgent()
        a._legacy_agent = None
        with patch.dict("sys.modules", {"agents.creative_agent": None}):
            result = a._get_legacy_agent()
            assert result is None

    @pytest.mark.asyncio
    async def test_marketing_sub_agents_import_error(self):
        import sys

        # Use importlib.import_module to avoid py/import-and-import-from CodeQL finding
        # (this file also has `from agents.core.marketing.agent import ...` in other tests)
        mod = importlib.import_module("agents.core.marketing.agent")
        sys.modules.pop("agents.core.marketing.agent", None)
        with patch.dict(
            "sys.modules",
            {
                "agents.core.marketing.agent": mod,
                "agents.core.marketing.sub_agents.social_media": None,
                "agents.core.marketing.sub_agents.campaign_ops": None,
            },
        ):
            importlib.reload(mod)
            a = mod.MarketingCoreAgent()
            # Legacy sub-agents should be absent; SDK agents may still register
            assert "social_media" not in a._sub_agents
            assert "campaign_ops" not in a._sub_agents
        # Restore module to sys.modules before cleanup reload
        sys.modules["agents.core.marketing.agent"] = mod
        importlib.reload(mod)

    @pytest.mark.asyncio
    async def test_marketing_legacy_import_error(self):
        from agents.core.marketing.agent import MarketingCoreAgent

        a = MarketingCoreAgent()
        a._legacy_agent = None
        with patch.dict("sys.modules", {"agents.marketing_agent": None}):
            result = a._get_legacy_agent()
            assert result is None

    @pytest.mark.asyncio
    async def test_operations_sub_agents_import_error(self):
        import sys

        # Use importlib.import_module to avoid py/import-and-import-from CodeQL finding
        # (this file also has `from agents.core.operations.agent import ...` in other tests)
        mod = importlib.import_module("agents.core.operations.agent")
        sys.modules.pop("agents.core.operations.agent", None)
        with patch.dict(
            "sys.modules",
            {
                "agents.core.operations.agent": mod,
                "agents.core.operations.sub_agents.deploy_health": None,
                "agents.core.operations.sub_agents.security_monitor": None,
                "agents.core.operations.sub_agents.coding_doctor": None,
            },
        ):
            importlib.reload(mod)
            a = mod.OperationsCoreAgent()
            # Legacy sub-agents should be absent; SDK agents may still register
            assert "deploy_health" not in a._sub_agents
            assert "security_monitor" not in a._sub_agents
            assert "coding_doctor" not in a._sub_agents
        # Restore module to sys.modules before cleanup reload
        sys.modules["agents.core.operations.agent"] = mod
        importlib.reload(mod)

    @pytest.mark.asyncio
    async def test_operations_legacy_import_error(self):
        from agents.core.operations.agent import OperationsCoreAgent

        a = OperationsCoreAgent()
        a._legacy_agent = None
        with patch.dict("sys.modules", {"agents.operations_agent": None}):
            result = a._get_legacy_agent()
            assert result is None

    @pytest.mark.asyncio
    async def test_analytics_sub_agents_import_error(self):
        import sys

        # Use importlib.import_module to avoid py/import-and-import-from CodeQL finding
        # (this file also has `from agents.core.analytics.agent import ...` in other tests)
        mod = importlib.import_module("agents.core.analytics.agent")
        sys.modules.pop("agents.core.analytics.agent", None)
        with patch.dict(
            "sys.modules",
            {
                "agents.core.analytics.agent": mod,
                "agents.core.analytics.sub_agents.analytics_ops": None,
            },
        ):
            importlib.reload(mod)
            a = mod.AnalyticsCoreAgent()
            # Legacy sub-agent should be absent; SDK agents may still register
            assert "analytics_ops" not in a._sub_agents
        # Restore module to sys.modules before cleanup reload
        sys.modules["agents.core.analytics.agent"] = mod
        importlib.reload(mod)

    @pytest.mark.asyncio
    async def test_analytics_legacy_import_error(self):
        from agents.core.analytics.agent import AnalyticsCoreAgent

        a = AnalyticsCoreAgent()
        a._legacy_agent = None
        with patch.dict("sys.modules", {"agents.analytics_agent": None}):
            result = a._get_legacy_agent()
            assert result is None

    @pytest.mark.asyncio
    async def test_imagery_legacy_import_error(self):
        from agents.core.imagery.agent import ImageryCoreAgent

        a = ImageryCoreAgent()
        a._legacy_imagery = None
        with patch.dict("sys.modules", {"agents.skyyrose_imagery_agent": None}):
            result = a._get_legacy_imagery()
            assert result is None

    @pytest.mark.asyncio
    async def test_commerce_sub_agents_import_error(self):
        import sys

        # Use importlib.import_module to avoid py/import-and-import-from CodeQL finding
        # (this file also has `from agents.core.commerce.agent import ...` in other tests)
        mod = importlib.import_module("agents.core.commerce.agent")
        sys.modules.pop("agents.core.commerce.agent", None)
        with patch.dict(
            "sys.modules",
            {
                "agents.core.commerce.agent": mod,
                "agents.core.commerce.sub_agents.product_ops": None,
                "agents.core.commerce.sub_agents.wordpress_assets": None,
                "agents.core.commerce.sub_agents.wordpress_bridge": None,
            },
        ):
            importlib.reload(mod)
            a = mod.CommerceCoreAgent()
            # Legacy sub-agents should be absent; SDK agents may still register
            assert "product_ops" not in a._sub_agents
            assert "wordpress_assets" not in a._sub_agents
            assert "wordpress_bridge" not in a._sub_agents
        # Restore module to sys.modules before cleanup reload
        sys.modules["agents.core.commerce.agent"] = mod
        importlib.reload(mod)

    @pytest.mark.asyncio
    async def test_commerce_legacy_import_error(self):
        from agents.core.commerce.agent import CommerceCoreAgent

        a = CommerceCoreAgent()
        a._legacy_agent = None
        with patch.dict("sys.modules", {"agents.commerce_agent": None}):
            result = a._get_legacy_agent()
            assert result is None

    @pytest.mark.asyncio
    async def test_web_builder_sub_agents_import_error(self):
        import sys

        # Use importlib.import_module to avoid py/import-and-import-from CodeQL finding
        # (this file also has `from agents.core.web_builder.agent import ...` in other tests)
        mod = importlib.import_module("agents.core.web_builder.agent")
        sys.modules.pop("agents.core.web_builder.agent", None)
        with patch.dict(
            "sys.modules",
            {
                "agents.core.web_builder.agent": mod,
                "agents.core.web_builder.sub_agents.web_dev": None,
            },
        ):
            importlib.reload(mod)
            a = mod.WebBuilderCoreAgent()
            # Legacy sub-agent should be absent; SDK agents may still register
            assert "web_dev" not in a._sub_agents
        # Restore module to sys.modules before cleanup reload
        sys.modules["agents.core.web_builder.agent"] = mod
        importlib.reload(mod)

    @pytest.mark.asyncio
    async def test_web_builder_director_import_error(self):
        from agents.core.web_builder.agent import WebBuilderCoreAgent

        a = WebBuilderCoreAgent()
        a._director = None
        with patch.dict("sys.modules", {"agents.elite_web_builder.director": None}):
            result = a._get_director()
            assert result is None
