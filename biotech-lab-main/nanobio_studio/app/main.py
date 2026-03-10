"""
FastAPI Application Setup

Main entry point for ML module REST API.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import get_settings, configure_logging
from .db.database import get_db
from .api.ml_router import router as ml_router


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    
    # Startup
    logger.info("Starting ML Module API")
    db = get_db()
    db.init_db()
    
    yield
    
    # Shutdown
    logger.info("Shutting down ML Module API")
    db.close()


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    settings = get_settings()
    configure_logging()
    
    app = FastAPI(
        title=settings.API_TITLE,
        version=settings.API_VERSION,
        docs_url="/docs",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(ml_router, prefix=settings.API_PREFIX)
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "name": settings.API_TITLE,
            "version": settings.API_VERSION,
            "status": "running",
        }
    
    logger.info("FastAPI application created")
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENV.value == "development",
        log_level=settings.LOG_LEVEL.lower(),
    )
