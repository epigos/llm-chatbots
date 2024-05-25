import fastapi

from app.routers.auth.endpoints import router as auth_router
from app.routers.bots.endpoints import router as bots_router
from app.routers.health.endpoints import router as health_router
from app.routers.uploads.endpoints import router as uploads_router
from app.routers.users.endpoints import router as users_router


def include_routers(app: fastapi.FastAPI) -> None:
    """
    Configure app routers
    """
    app.include_router(health_router)
    app.include_router(bots_router)
    app.include_router(uploads_router)
    app.include_router(auth_router)
    app.include_router(users_router)
