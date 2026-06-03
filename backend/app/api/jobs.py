from fastapi import APIRouter
from app.services.job_service import JobService

router = APIRouter()
service = JobService()


@router.get("/{job_id}")
def get_job(job_id: str):
    return service.get_job(job_id)
