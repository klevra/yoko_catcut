from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Literal, Optional


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


class JobStatusUpdate(BaseModel):
    status: str


class SubtitleSegmentUpdate(BaseModel):
    id: int
    start: float
    end: float
    text: str
    speaker_id: Optional[str] = None


class SubtitleUpdate(BaseModel):
    segments: List[SubtitleSegmentUpdate]


class SubtitleGenerateRequest(BaseModel):
    language: Optional[str] = None
    selected_speakers: List[str] = Field(default_factory=list)


class EditSegment(BaseModel):
    start: float
    end: float
    comment: str = ""


class ProcessingOptions(BaseModel):
    remove_silence: bool = False
    speed_up_excluded: bool = False
    excluded_speed: Literal[2, 4, 8, 16] = 2
    assembly_only: bool = False
    remove_background_music: bool = False
    add_background_music: bool = False
    background_music_volume: float = 0.22


class ExportRequest(BaseModel):
    aspect_ratio: str = "original"
    editor_tool: str = "generic"
    segments: List[EditSegment] = Field(default_factory=list)
    burn_subtitles: bool = True
    processing_options: ProcessingOptions = Field(default_factory=ProcessingOptions)


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
