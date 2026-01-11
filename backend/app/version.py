from fastapi import APIRouter

router = APIRouter()

__version__ = "0.1.0"


@router.get("/version")
async def get_version():
    """Get API version information."""
    return {"version": __version__, "api": "v1", "status": "active"}
