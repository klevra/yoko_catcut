from fastapi import APIRouter, UploadFile, File, Form
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
    saved_path = await storage_service.save_original(user_id, project_name, file)
    job = job_service.create_job(user_id, project_name, "UPLOAD", {"path": saved_path})
    return {
        "message": "uploaded",
        "path": saved_path,
        "job": job,
    }
