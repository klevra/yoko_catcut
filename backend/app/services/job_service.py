from pathlib import Path
from app.models.models import Job, JobStatus, JobType
from app.repositories.job_repository import JobRepository
from datetime import datetime
import uuid


class JobService:
    """Job 관리 서비스"""

    def __init__(self):
        self.repository = JobRepository()

    def create_job(
        self,
        user_id: str,
        project_name: str,
        job_type: str,
        metadata: dict = None,
    ) -> dict:
        """Job 생성"""
        job_id = str(uuid.uuid4())
        job = Job(
            job_id=job_id,
            user_id=user_id,
            project_name=project_name,
            job_type=JobType(job_type),
            status=JobStatus.QUEUED,
            metadata=metadata or {},
        )
        self.repository.create(job)
        return {
            "job_id": job.job_id,
            "user_id": job.user_id,
            "project_name": job.project_name,
            "job_type": job.job_type.value,
            "status": job.status.value,
            "metadata": job.metadata,
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat(),
        }

    def get_job(self, job_id: str) -> dict:
        """Job 조회"""
        job = self.repository.read(job_id)
        if not job:
            raise ValueError(f"Job not found: {job_id}")
        return {
            "job_id": job.job_id,
            "user_id": job.user_id,
            "project_name": job.project_name,
            "job_type": job.job_type.value,
            "status": job.status.value,
            "metadata": job.metadata,
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat(),
        }

    def list_jobs(self, user_id: str, project_name: str) -> list:
        """프로젝트의 Job 목록 조회"""
        jobs = self.repository.list_by_project(user_id, project_name)
        return [
            {
                "job_id": job.job_id,
                "user_id": job.user_id,
                "project_name": job.project_name,
                "job_type": job.job_type.value,
                "status": job.status.value,
                "metadata": job.metadata,
                "created_at": job.created_at.isoformat(),
                "updated_at": job.updated_at.isoformat(),
            }
            for job in jobs
        ]

    def update_job_status(self, job_id: str, status: str) -> dict:
        """Job 상태 업데이트"""
        job = self.repository.read(job_id)
        if not job:
            raise ValueError(f"Job not found: {job_id}")

        job.status = JobStatus(status)
        job.updated_at = datetime.now()
        self.repository.update(job)

        return {
            "job_id": job.job_id,
            "user_id": job.user_id,
            "project_name": job.project_name,
            "job_type": job.job_type.value,
            "status": job.status.value,
            "metadata": job.metadata,
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat(),
        }

    def cancel_job(self, job_id: str) -> dict:
        """Job 취소"""
        job = self.repository.read(job_id)
        if not job:
            raise ValueError(f"Job not found: {job_id}")

        job.status = JobStatus.CANCELED
        job.updated_at = datetime.now()
        self.repository.update(job)

        return {
            "job_id": job.job_id,
            "user_id": job.user_id,
            "project_name": job.project_name,
            "job_type": job.job_type.value,
            "status": job.status.value,
            "metadata": job.metadata,
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat(),
        }
