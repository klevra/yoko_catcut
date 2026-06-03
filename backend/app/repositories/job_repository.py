from typing import List, Optional
from app.models.models import Job, JobStatus, JobType
import json
import uuid
from pathlib import Path


class JobRepository:
    """Job 데이터 영속성 관리"""

    def __init__(self, storage_path: str = "./data/jobs"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _get_job_file(self, job_id: str) -> Path:
        return self.storage_path / f"{job_id}.json"

    def create(self, job: Job) -> Job:
        """Job 생성"""
        file_path = self._get_job_file(job.job_id)
        data = {
            "job_id": job.job_id,
            "user_id": job.user_id,
            "project_name": job.project_name,
            "job_type": job.job_type.value,
            "status": job.status.value,
            "metadata": job.metadata,
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat(),
        }
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        return job

    def read(self, job_id: str) -> Optional[Job]:
        """Job 조회"""
        file_path = self._get_job_file(job_id)
        if not file_path.exists():
            return None
        with open(file_path, "r") as f:
            data = json.load(f)
        return Job(
            job_id=data["job_id"],
            user_id=data["user_id"],
            project_name=data["project_name"],
            job_type=JobType(data["job_type"]),
            status=JobStatus(data["status"]),
            metadata=data["metadata"],
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def list_by_project(self, user_id: str, project_name: str) -> List[Job]:
        """프로젝트의 모든 Job 조회"""
        jobs = []
        for file in self.storage_path.glob("*.json"):
            with open(file, "r") as f:
                data = json.load(f)
            if (
                data.get("user_id") == user_id
                and data.get("project_name") == project_name
            ):
                jobs.append(
                    Job(
                        job_id=data["job_id"],
                        user_id=data["user_id"],
                        project_name=data["project_name"],
                        job_type=JobType(data["job_type"]),
                        status=JobStatus(data["status"]),
                        metadata=data["metadata"],
                        created_at=data.get("created_at"),
                        updated_at=data.get("updated_at"),
                    )
                )
        return jobs

    def update(self, job: Job) -> Job:
        """Job 업데이트"""
        return self.create(job)

    def delete(self, job_id: str) -> bool:
        """Job 삭제"""
        file_path = self._get_job_file(job_id)
        if file_path.exists():
            file_path.unlink()
            return True
        return False
