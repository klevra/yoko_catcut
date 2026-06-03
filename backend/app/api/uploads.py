from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.schemas.project import UploadResponse
from app.services.storage_service import StorageService
from app.services.job_service import JobService

router = APIRouter()
storage_service = StorageService()
job_service = JobService()


@router.post("")
async def upload_file(
    user_id: str = Form(...),
    project_name: str = Form(...),
    file: UploadFile = File(...),
):
    """파일 업로드"""
    try:
        # 파일 저장
        upload_info = await storage_service.save_original(user_id, project_name, file)

        # Job 생성
        job = job_service.create_job(
            user_id,
            project_name,
            "UPLOAD",
            {"upload_id": upload_info["upload_id"], "path": upload_info["path"]},
        )

        return {
            "message": "uploaded",
            "upload": upload_info,
            "job": job,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{upload_id}")
def get_upload_info(upload_id: str):
    """업로드 파일 정보 조회"""
    try:
        # TODO: Upload Repository에서 조회
        raise HTTPException(status_code=501, detail="Not implemented")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
