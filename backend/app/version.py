from typing import Dict

from fastapi import APIRouter

router = APIRouter()

__version__ = "0.2.4"


@router.get("/version")
async def get_version() -> Dict[str, str]:
    """Get API version information."""
    return {"version": __version__, "api": "v1", "status": "active"}
