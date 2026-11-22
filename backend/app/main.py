from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import check_db_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME
    }

@app.get("/health/ready")
async def readiness_check():
    db_healthy = await check_db_connection()
    if not db_healthy:
        return {
            "status": "degraded",
            "database": "disconnected"
        }
    
    return {
        "status": "ready",
        "database": "connected",
        "neon_branch": settings.NEON_BRANCH
    }