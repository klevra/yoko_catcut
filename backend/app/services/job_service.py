from datetime import datetime
from uuid import uuid4


class JobService:
    _jobs: dict[str, dict] = {}

    def create_job(self, user_id: str, project_name: str, job_type: str, payload: dict) -> dict:
        job_id = str(uuid4())
        job = {
            "job_id": job_id,
            "user_id": user_id,
            "project_name": project_name,
            "job_type": job_type,
            "status": "QUEUED",
            "payload": payload,
            "created_at": datetime.utcnow().isoformat(),
        }
        self._jobs[job_id] = job
        return job

    def get_job(self, job_id: str) -> dict:
        return self._jobs.get(job_id, {"job_id": job_id, "status": "NOT_FOUND"})
