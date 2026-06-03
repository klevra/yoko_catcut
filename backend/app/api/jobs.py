from fastapi import APIRouter, HTTPException
from app.services.job_service import JobService

router = APIRouter()
job_service = JobService()


@router.get("/{job_id}")
def get_job(job_id: str):
    """Job 상태 조회"""
    try:
        return job_service.get_job(job_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("")
def list_jobs(user_id: str, project_name: str):
    """프로젝트의 Job 목록 조회"""
    try:
        return job_service.list_jobs(user_id, project_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{job_id}/status")
def update_job_status(job_id: str, status: str):
    """Job 상태 업데이트"""
    try:
        return job_service.update_job_status(job_id, status)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{job_id}/cancel")
def cancel_job(job_id: str):
    """Job 취소"""
    try:
        return job_service.cancel_job(job_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
