"""
Creative Operations Hub — SkyyRose Elite Studio.

Unified LangGraph router for 14 creative intents:
product renders, 3D models, social packs, product copy, character sheets,
scene compositing, virtual try-on, full product launches, design ideation,
mockups, collection plans, tech packs, moodboards, colorway exploration.

"""

from __future__ import annotations

__all__ = [
    "run_creative",
    "CreativeIntent",
    "CreativeOperationState",
    "create_initial_state",
]


def __getattr__(name: str):
    """Preserve public exports without importing execution for report readers."""
    if name == "run_creative":
        from .runner import run_creative

        return run_creative
    if name in {"CreativeIntent", "CreativeOperationState", "create_initial_state"}:
        from . import state

        return getattr(state, name)
    raise AttributeError(name)
