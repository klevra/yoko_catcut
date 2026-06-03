from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, projects, uploads, jobs
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Yoko CatCut API",
    version="0.1.0",
    description="AI video editing platform backend"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(uploads.router, prefix="/api/v1/uploads", tags=["uploads"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])
