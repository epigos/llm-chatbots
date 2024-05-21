from fastapi import APIRouter

router = APIRouter(tags=["Health checks"])


@router.get("/healthz/", include_in_schema=False)
async def healthz() -> str:
    """Health check endpoint"""
    return "ok"
