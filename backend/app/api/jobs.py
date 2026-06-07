from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import current_user
from app.schemas.project import JobStatusUpdate
from app.services.job_service import JobService

router = APIRouter()
job_service = JobService()


@router.get("/{job_id}")
def get_job(job_id: str, user_id: str = Depends(current_user)):
    """Job 상태 조회"""
    try:
        job = job_service.get_job(job_id)
        if job["user_id"] != user_id:
            raise ValueError("You can only access your own jobs")
        return job
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("")
def list_jobs(
    user_id: str,
    project_name: str,
    authenticated: str = Depends(current_user),
):
    """프로젝트의 Job 목록 조회"""
    try:
        return job_service.list_jobs(user_id, project_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{job_id}/status")
def update_job_status(
    job_id: str,
    payload: JobStatusUpdate,
    user_id: str = Depends(current_user),
):
    """Job 상태 업데이트"""
    try:
        job = job_service.get_job(job_id)
        if job["user_id"] != user_id:
            raise ValueError("You can only update your own jobs")
        return job_service.update_job_status(job_id, payload.status)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{job_id}/cancel")
def cancel_job(job_id: str, user_id: str = Depends(current_user)):
    """Job 취소"""
    try:
        job = job_service.get_job(job_id)
        if job["user_id"] != user_id:
            raise ValueError("You can only cancel your own jobs")
        return job_service.cancel_job(job_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        if user_id != authenticated:
            raise ValueError("You can only list your own jobs")
