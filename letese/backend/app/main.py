# Main FastAPI app for LETESE
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.routers import auth, cases

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 LETESE API starting up...")
    yield
    logger.info("👋 LETESE API shutting down...")


app = FastAPI(
    title="LETESE API",
    description="AI-powered Legal Practice Management SaaS",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - allow frontend apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )


# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": "LETESE API",
        "version": "1.0.0"
    }


# Include routers
app.include_router(auth.router)
app.include_router(cases.router)


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "LETESE API v1.0.0",
        "docs": "/docs",
        "health": "/health"
    }