"""Compatibility router export; standalone hosts use skyyrose.godmode_runtime.api.

Importing api.v1 itself eagerly loads legacy commerce routers. Keep the execution
host independent from those optional modules by launching the canonical module.
"""

from skyyrose.godmode_runtime.api import create_app, get_runtime, router

__all__ = ["create_app", "get_runtime", "router"]
