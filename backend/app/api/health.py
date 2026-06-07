from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter()


@router.get("/health")
def health_check():
    settings = get_settings()
    return {
        "status": "ok",
        "service": "yoko_catcut",
        "version": "0.6.0",
        "runtime_os": settings.runtime_os,
        "detected_os": settings.detected_os,
    }
