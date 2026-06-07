from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, health, projects, uploads, jobs
from app.core.config import get_settings
from app.services.job_processor import JobProcessor

settings = get_settings()
job_processor = JobProcessor()


@asynccontextmanager
async def lifespan(_: FastAPI):
    job_processor.start()
    yield
    job_processor.stop()

app = FastAPI(
    title="Yoko CatCut API",
    version="0.5.1",
    description="AI video editing platform backend",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(uploads.router, prefix="/api/v1/uploads", tags=["uploads"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])
