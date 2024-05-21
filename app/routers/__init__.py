import fastapi

from app.routers.health.endpoints import router as health_router


def include_routers(app: fastapi.FastAPI) -> None:
    """
    Configure app routers
    """
    app.include_router(health_router)
