"""Tests for AI Space templates."""

from scripts.ai_config import AIConfig


def test_render_trainer_template_contains_dataset():
    """Rendered template includes the configured dataset name."""
    from scripts.ai_templates import render_trainer_app

    config = AIConfig(dataset="damBruh/skyyrose-lora-dataset-v5")
    rendered = render_trainer_app(config)
    assert "damBruh/skyyrose-lora-dataset-v5" in rendered
    assert "gradio" in rendered.lower()


def test_render_trainer_template_respects_steps():
    """Rendered template uses configured step count."""
    from scripts.ai_templates import render_trainer_app

    config = AIConfig(steps=500)
    rendered = render_trainer_app(config)
    assert "--max_train_steps=500" in rendered


def test_render_trainer_template_respects_resolution():
    """Rendered template uses configured resolution."""
    from scripts.ai_templates import render_trainer_app

    config = AIConfig(resolution=512)
    rendered = render_trainer_app(config)
    assert "--resolution=512" in rendered


def test_render_requirements():
    """render_requirements() returns valid requirements.txt content."""
    from scripts.ai_templates import render_requirements

    reqs = render_requirements()
    assert "gradio" in reqs
    assert "huggingface_hub" in reqs
    assert "torch" in reqs


def _hub_requirement(lines):
    from packaging.requirements import Requirement

    specs = [line.split("#", 1)[0].strip() for line in lines]
    reqs = [Requirement(spec) for spec in specs if spec and not spec.startswith("-")]
    (hub,) = [r for r in reqs if r.name.lower().replace("_", "-") == "huggingface-hub"]
    return hub


def test_trainer_requirements_keep_hub_on_1x_for_gradio():
    """gradio 5.50 requires huggingface-hub>=0.33.5,<2; hub 2.x also swaps httpx for httpx2."""
    from scripts.ai_templates import render_requirements

    hub = _hub_requirement(render_requirements().splitlines())
    assert "1.33.0" in hub.specifier
    assert "0.33.5" in hub.specifier
    assert "0.33.4" not in hub.specifier
    assert "2.0.0" not in hub.specifier


def test_repo_declarations_cap_hub_below_2():
    """Every place the repo declares huggingface-hub stays off the httpx2-based 2.x line."""
    import tomllib
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    declared = [
        dep
        for deps in pyproject["project"]["optional-dependencies"].values()
        for dep in deps
        if dep.lower().replace("_", "-").startswith("huggingface-hub")
    ]
    trellis = (root / "requirements-trellis.txt").read_text(encoding="utf-8").splitlines()
    for hub in [_hub_requirement(declared), _hub_requirement(trellis)]:
        assert "1.33.0" in hub.specifier
        assert "2.0.0" not in hub.specifier
