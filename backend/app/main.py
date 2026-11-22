from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.exceptions import BreatheSmartException
from app.core.logging import setup_logging
from app.db.session import check_db_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN, "http://127.0.0.1:5173", "https://breathesmart-ai.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(BreatheSmartException)
async def domain_exception_handler(request: Request, e: BreatheSmartException):
    status_code = status.HTTP_400_BAD_REQUEST
    if e.code in ("INVALID_SESSION", "SESSION_EXPIRED"):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif e.code =="CSRF_VALIDATION_FAILED":
        status_code = status.HTTP_403_FORBIDDEN
    elif e.code in ("AIR_QUALITY_PROVIDER_ERROR", "AI_PROVIDER_ERROR"):
        status_code = status.HTTP_502_BAD_GATEWAY
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": e.code,
                "message": e.message,
                "details": e.details
            }
        },
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
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "degraded",
                "database": "disconnected"
            },
        )
    
    return {
        "status": "ready",
        "database": "connected",
        "neon_branch": settings.NEON_BRANCH
    }