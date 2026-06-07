from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    ANALYZING = "ANALYZING"
    SUBTITLE_GENERATING = "SUBTITLE_GENERATING"
    HIGHLIGHT_EXTRACTING = "HIGHLIGHT_EXTRACTING"
    RENDERING = "RENDERING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"


class JobType(str, Enum):
    UPLOAD = "UPLOAD"
    ANALYZE = "ANALYZE"
    SUBTITLE = "SUBTITLE"
    SPEECH_ANALYSIS = "SPEECH_ANALYSIS"
    HIGHLIGHT = "HIGHLIGHT"
    SHORTS = "SHORTS"
    THUMBNAIL = "THUMBNAIL"
    YOUTUBE = "YOUTUBE"
    EXPORT = "EXPORT"


class Project:
    def __init__(
        self,
        user_id: str,
        project_name: str,
        path: str,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.user_id = user_id
        self.project_name = project_name
        self.path = path
        self.created_at = self._parse_datetime(created_at)
        self.updated_at = self._parse_datetime(updated_at)

    @staticmethod
    def _parse_datetime(value: Optional[datetime]) -> datetime:
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return value or datetime.now()


class Job:
    def __init__(
        self,
        job_id: str,
        user_id: str,
        project_name: str,
        job_type: JobType,
        status: JobStatus = JobStatus.QUEUED,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.job_id = job_id
        self.user_id = user_id
        self.project_name = project_name
        self.job_type = job_type
        self.status = status
        self.metadata = metadata or {}
        self.created_at = self._parse_datetime(created_at)
        self.updated_at = self._parse_datetime(updated_at)

    @staticmethod
    def _parse_datetime(value: Optional[datetime]) -> datetime:
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return value or datetime.now()


class Upload:
    def __init__(
        self,
        upload_id: str,
        user_id: str,
        project_name: str,
        filename: str,
        path: str,
        file_size: int,
        duration: Optional[float] = None,
        created_at: Optional[datetime] = None,
    ):
        self.upload_id = upload_id
        self.user_id = user_id
        self.project_name = project_name
        self.filename = filename
        self.path = path
        self.file_size = file_size
        self.duration = duration
        self.created_at = self._parse_datetime(created_at)

    @staticmethod
    def _parse_datetime(value: Optional[datetime]) -> datetime:
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return value or datetime.now()
