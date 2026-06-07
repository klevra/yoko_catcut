import threading
import time
import traceback
from app.models.models import JobStatus
from app.repositories.job_repository import JobRepository
from app.services.job_service import JobService


class JobProcessor:
    """Background job processor for queued tasks."""

    def __init__(self):
        self.repository = JobRepository()
        self.job_service = JobService()
        self._thread = None
        self._stopped = False

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stopped = False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stopped = True
        if self._thread is not None:
            self._thread.join(timeout=1)

    def _run(self) -> None:
        while not self._stopped:
            try:
                self._process_queue()
            except Exception:
                traceback.print_exc()
            time.sleep(2)

    def _process_queue(self) -> None:
        queued_jobs = self.repository.list_by_status(JobStatus.QUEUED)
        for job in queued_jobs:
            try:
                self.job_service.process_job(job)
            except Exception:
                traceback.print_exc()
