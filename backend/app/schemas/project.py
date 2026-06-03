from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ProjectCreate(BaseModel):
    user_id: str
    project_name: str


class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None


class ProjectResponse(BaseModel):
    user_id: str
    project_name: str
    path: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobStatus(BaseModel):
    job_id: str
    user_id: str
    project_name: str
    job_type: str
    status: str
    metadata: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    upload_id: str
    user_id: str
    project_name: str
    filename: str
    path: str
    file_size: int
    duration: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class WorkspaceInfo(BaseModel):
    user_id: str
    project_name: str
    original_path: str
    generated_path: str
    metadata_path: str
    jobs_path: str

