from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "yoko_catcut",
        "version": "0.1.1"
    }
