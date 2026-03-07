from fastapi import FastAPI

from src.middleware.error_middleware import attach_error_handlers
from src.modules.auth.auth_controller import router as auth_router
from src.modules.catalogs.catalogs_controller import router as catalogs_router
from src.modules.profile.profile_controller import router as profile_router
from src.modules.watchlist.watchlist_controller import router as watchlist_router


def create_app() -> FastAPI:
    app = FastAPI(title="Whatflix Auth API")
    attach_error_handlers(app)
    app.include_router(auth_router)
    app.include_router(profile_router)
    app.include_router(watchlist_router)
    app.include_router(catalogs_router)

    @app.get("/health")
    def health() -> dict:
        """
        Health check endpoint.

        Example:
            /health {}
        """
        return {"ok": True}

    return app
