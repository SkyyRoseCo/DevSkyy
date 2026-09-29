"""Tests for Coordinator — pipeline orchestration."""

from unittest.mock import MagicMock, patch

import pytest

from skyyrose.elite_studio.coordinator import Coordinator, NullLogger

from .conftest import (
    make_generation_result,
    make_production_result,
    make_quality_verification,
    make_synthesized_vision,
)


@pytest.fixture
def mock_vision():
    return MagicMock()


@pytest.fixture
def mock_generator():
    return MagicMock()


@pytest.fixture
def mock_quality():
    return MagicMock()


@pytest.fixture
def coordinator(mock_vision, mock_generator, mock_quality):
    return Coordinator(
        vision=mock_vision,
        generator=mock_generator,
        quality=mock_quality,
        logger=NullLogger(),
    )


class TestCoordinatorProduce:
    def test_success_pipeline(self, coordinator, mock_vision, mock_generator, mock_quality):
        mock_vision.analyze.return_value = make_synthesized_vision()
        mock_generator.generate.return_value = make_generation_result()
        mock_quality.verify.return_value = make_quality_verification()

        result = coordinator.produce("br-001")
        assert result.status == "success"
        assert result.output_path == "/tmp/br-001-model-front-gemini.jpg"
        assert result.vision.provider_count == 2
        assert result.quality.overall_status == "pass"

    def test_vision_failure(self, coordinator, mock_vision):
        mock_vision.analyze.return_value = make_synthesized_vision(
            success=False,
            error="All providers failed",
            unified_spec="",
            providers_used=(),
        )

        result = coordinator.produce("br-001")
        assert result.status == "error"
        assert result.step == "vision"
        assert "All providers failed" in result.error

    def test_generation_failure(self, coordinator, mock_vision, mock_generator):
        mock_vision.analyze.return_value = make_synthesized_vision(
            providers_used=("gemini",),
        )
        mock_generator.generate.return_value = make_generation_result(
            success=False,
            error="Timeout",
            output_path="",
        )

        result = coordinator.produce("br-001")
        assert result.status == "error"
        assert result.step == "generation"

    def test_qc_failure_blocks_production(
        self, coordinator, mock_vision, mock_generator, mock_quality
    ):
        """A generated file is retained, but missing QC cannot approve production."""
        mock_vision.analyze.return_value = make_synthesized_vision(
            providers_used=("gemini",),
        )
        mock_generator.generate.return_value = make_generation_result()
        mock_quality.verify.return_value = make_quality_verification(
            success=False,
            overall_status="",
            recommendation="",
            error="Claude overloaded",
        )

        result = coordinator.produce("br-001")
        assert result.status == "error"
        assert result.step == "quality"
        assert result.output_path
        assert not result.quality.success

    def test_generator_receives_spec(self, coordinator, mock_vision, mock_generator, mock_quality):
        mock_vision.analyze.return_value = make_synthesized_vision(
            unified_spec="THE EXACT SPEC",
            providers_used=("gemini",),
        )
        mock_generator.generate.return_value = make_generation_result(
            output_path="/tmp/test.jpg",
        )
        mock_quality.verify.return_value = make_quality_verification()

        coordinator.produce("br-001")

        # Coordinator threads its RunBudget (None when unconfigured) through
        # to the generator so the per-call budget gate has an anchor.
        mock_generator.generate.assert_called_once_with(
            sku="br-001",
            view="front",
            generation_spec="THE EXACT SPEC",
            budget=None,
        )


class TestCoordinatorBatch:
    @patch("skyyrose.elite_studio.coordinator.time.sleep")
    @patch("skyyrose.elite_studio.coordinator.discover_all_skus")
    def test_batch_all(
        self, mock_discover, mock_sleep, coordinator, mock_vision, mock_generator, mock_quality
    ):
        mock_discover.return_value = ["br-001", "br-002"]

        mock_vision.analyze.return_value = make_synthesized_vision(
            providers_used=("gemini",),
        )
        mock_generator.generate.return_value = make_generation_result()
        mock_quality.verify.return_value = make_quality_verification()

        with patch("skyyrose.elite_studio.coordinator.OUTPUT_DIR", MagicMock()):
            with patch.object(coordinator, "_write_report"):
                results = coordinator.produce_batch(
                    skus=["br-001", "br-002"],
                    skip_existing=False,
                )

        assert len(results) == 2
        assert all(r.status == "success" for r in results)

    def test_batch_handles_exception(self, coordinator, mock_vision):
        mock_vision.analyze.side_effect = RuntimeError("Unexpected")

        with patch("skyyrose.elite_studio.coordinator.time.sleep"):
            with patch("skyyrose.elite_studio.coordinator.OUTPUT_DIR", MagicMock()):
                with patch.object(coordinator, "_write_report"):
                    results = coordinator.produce_batch(
                        skus=["br-001"],
                        skip_existing=False,
                    )

        assert len(results) == 1
        assert results[0].status == "error"


class TestCoordinatorBatchSkipExisting:
    @patch("skyyrose.elite_studio.coordinator.time.sleep")
    def test_skip_existing_filters(
        self, mock_sleep, coordinator, mock_vision, mock_generator, mock_quality, tmp_path
    ):
        mock_vision.analyze.return_value = make_synthesized_vision(
            providers_used=("gemini",),
        )
        mock_generator.generate.return_value = make_generation_result()
        mock_quality.verify.return_value = make_quality_verification()

        # Create real output dir where br-001 already exists
        br001_dir = tmp_path / "br-001"
        br001_dir.mkdir()
        (br001_dir / "br-001-model-front-gemini.jpg").write_bytes(b"\xff\xd8")

        with patch("skyyrose.elite_studio.coordinator.OUTPUT_DIR", tmp_path):
            with patch.object(coordinator, "_write_report"):
                with patch.object(coordinator, "_print_summary"):
                    results = coordinator.produce_batch(
                        skus=["br-001", "br-002"],
                        skip_existing=True,
                    )

        # Only br-002 should be processed (br-001 was skipped)
        assert len(results) == 1
        mock_vision.analyze.assert_called_once()


class TestWriteReport:
    def test_writes_json_report(self, coordinator, tmp_path):
        results = [
            make_production_result(sku="br-001"),
            make_production_result(sku="br-002", status="error", error="Timeout"),
        ]

        with patch("skyyrose.elite_studio.coordinator.OUTPUT_DIR", tmp_path):
            coordinator._write_report(results)

        report_path = tmp_path / "BATCH_REPORT.json"
        assert report_path.exists()

        import json

        data = json.loads(report_path.read_text())
        assert len(data) == 2
        assert data[0]["id"] == "br-001"
        assert data[0]["status"] == "success"
        assert data[1]["id"] == "br-002"
        assert data[1]["status"] == "error"
        assert data[1]["error"] == "Timeout"


class TestPrintSummary:
    def test_summary_does_not_crash(self, coordinator):
        """PrintSummary should handle various result combinations."""
        results = [
            make_production_result(sku="br-001"),
            make_production_result(sku="br-002", status="error"),
        ]
        # NullLogger absorbs output — just verify no exceptions
        coordinator._print_summary(results)


class TestCoordinatorInit:
    def test_default_agents(self):
        coord = Coordinator()
        from skyyrose.elite_studio.agents.generator_agent import GeneratorAgent
        from skyyrose.elite_studio.agents.quality_agent import QualityAgent
        from skyyrose.elite_studio.agents.vision_agent import VisionAgent

        assert isinstance(coord.vision, VisionAgent)
        assert isinstance(coord.generator, GeneratorAgent)
        assert isinstance(coord.quality, QualityAgent)

    def test_custom_agents(self):
        mock_v = MagicMock()
        mock_g = MagicMock()
        mock_q = MagicMock()
        coord = Coordinator(vision=mock_v, generator=mock_g, quality=mock_q)
        assert coord.vision is mock_v
        assert coord.generator is mock_g
        assert coord.quality is mock_q

    def test_null_logger(self):
        coord = Coordinator(logger=NullLogger())
        assert isinstance(coord.log, NullLogger)
