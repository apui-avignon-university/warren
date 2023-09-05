"""Warren API v1 tdbp router."""

import logging

from fastapi import APIRouter

router = APIRouter(
    prefix="/tdbp",
)

logger = logging.getLogger(__name__)


@router.get("/test")
async def test():
    """A simple test endpoint."""
    return "ok"
