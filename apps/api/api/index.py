"""Vercel Python serverless entrypoint.

Vercel detects the ASGI ``app`` object in this module and serves it. All routes
are funneled here via the rewrite in ``vercel.json``. The project root is added
to ``sys.path`` so ``src`` resolves the same way it does under ``fastapi run``.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app  # noqa: E402

__all__ = ["app"]
