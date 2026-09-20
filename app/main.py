"""DocGen AI - Main FastAPI Application

AI-powered document generator for small businesses.
Generates professional proposals, invoices, reports, SOPs, and contracts.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.database import init_db
from app.routers import documents, auth, billing

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    init_db()
    print("[OK] Database initialized")
    print("[OK] DocGen AI is running at http://localhost:8000")
    yield


app = FastAPI(
    title="DocGen AI",
    description="AI-powered professional document generator for small businesses",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware - allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(auth.router)
app.include_router(billing.router)
app.include_router(documents.router)

# Serve frontend static files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "app": "DocGen AI", "version": "1.0.0"}
