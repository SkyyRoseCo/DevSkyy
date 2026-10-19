"""FastAPI surface for Blender render jobs.

Mount this router in ``main_enterprise.py`` exactly like ``api/v1/clothing_3d``:

.. code-block:: python

    from api.v1.render_jobs.router import router as render_jobs_router
    app.include_router(render_jobs_router, prefix="/api/v1")

The router declares its own ``/render-jobs`` prefix (v1 layer convention), so the final
paths are ``/api/v1/render-jobs``, ``/api/v1/render-jobs/{job_id}`` and
``/api/v1/render-jobs/health``.
"""

from api.v1.render_jobs.router import router

__all__ = ["router"]
