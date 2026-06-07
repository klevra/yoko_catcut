from pathlib import Path
from app.models.models import Job, JobStatus, JobType
from app.repositories.job_repository import JobRepository
from app.services.ffmpeg_service import FfmpegService
from app.services.subtitle_service import SubtitleService
from app.services.speech_analysis_service import SpeechAnalysisService
from app.services.catcut_service import CatCutAdapter
from app.services.export_service import ExportService
from app.core.config import get_settings
from datetime import datetime
import uuid
import json


class JobService:
    """Job 관리 서비스"""

    def __init__(self):
        self.repository = JobRepository()
        self.settings = get_settings()
        self.workspace_root = Path(self.settings.workspace_root)
        self.ffmpeg_service = FfmpegService()
        self.subtitle_service = SubtitleService()
        self.speech_analysis_service = SpeechAnalysisService()
        self.catcut_service = CatCutAdapter()
        self.export_service = ExportService()

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

    def process_job(self, job: Job) -> dict:
        """Process a queued job with a background worker."""
        if job.status != JobStatus.QUEUED:
            return self.get_job(job.job_id)

        try:
            if job.job_type == JobType.UPLOAD:
                self._complete_upload(job)
            elif job.job_type == JobType.ANALYZE:
                self._process_analysis(job)
            elif job.job_type == JobType.SUBTITLE:
                self._process_subtitle(job)
            elif job.job_type == JobType.SPEECH_ANALYSIS:
                self._process_speech_analysis(job)
            elif job.job_type == JobType.HIGHLIGHT:
                self._process_highlight(job)
            elif job.job_type == JobType.SHORTS:
                self._process_shorts(job)
            elif job.job_type == JobType.THUMBNAIL:
                self._process_thumbnail(job)
            elif job.job_type == JobType.EXPORT:
                self._process_export(job)
            else:
                self._mark_job_failed(job, f"Unsupported job type: {job.job_type.value}")
        except Exception as exc:
            self._mark_job_failed(job, str(exc))
        return self.get_job(job.job_id)

    def _complete_upload(self, job: Job) -> None:
        self._update_status(job, JobStatus.COMPLETED)
        self._write_metadata(job, {
            "type": "upload",
            "upload_id": job.metadata.get("upload_id"),
            "path": job.metadata.get("path"),
        })

    def _process_analysis(self, job: Job) -> None:
        self._update_status(job, JobStatus.ANALYZING)
        source_path = self._resolve_source_path(job)
        result = self.ffmpeg_service.probe(str(source_path))
        output = self._write_metadata(job, {
            "type": "analysis",
            "probe": result,
        })
        job.metadata["analysis_output"] = str(output)
        self._update_status(job, JobStatus.COMPLETED)

    def _process_subtitle(self, job: Job) -> None:
        self._update_status(job, JobStatus.SUBTITLE_GENERATING)
        source_path = self._resolve_source_path(job)
        output_dir = (
            self.workspace_root
            / job.user_id
            / job.project_name
            / "generated"
            / "subtitle"
        )
        selected_speakers = job.metadata.get("selected_speakers", [])
        if selected_speakers:
            analysis_path = (
                output_dir / f'{job.metadata["upload_id"]}_analysis.json'
            )
            if not analysis_path.is_file():
                raise FileNotFoundError("Run speech and speaker analysis first")
            with analysis_path.open("r", encoding="utf-8") as file:
                analysis = json.load(file)
            segments = self.speech_analysis_service.create_subtitles(
                analysis,
                selected_speakers,
            )
            result = self.subtitle_service.save(
                output_dir,
                job.metadata["upload_id"],
                {
                    "upload_id": job.metadata["upload_id"],
                    "language": analysis["language"],
                    "language_probability": analysis["language_probability"],
                    "duration": analysis.get("duration"),
                    "selected_speakers": selected_speakers,
                    "segments": segments,
                },
            )
        else:
            result = self.subtitle_service.generate(
                str(source_path),
                output_dir,
                job.metadata["upload_id"],
                job.metadata.get("language"),
            )
        job.metadata["subtitle_files"] = result
        self._update_status(job, JobStatus.COMPLETED)

    def _process_speech_analysis(self, job: Job) -> None:
        self._update_status(job, JobStatus.ANALYZING)
        source_path = self._resolve_source_path(job)
        result = self.speech_analysis_service.analyze(
            str(source_path),
            (
                self.workspace_root
                / job.user_id
                / job.project_name
                / "generated"
                / "subtitle"
            ),
            job.metadata["upload_id"],
            job.metadata.get("language"),
        )
        job.metadata["speech_analysis"] = result
        self._update_status(job, JobStatus.COMPLETED)

    def _process_highlight(self, job: Job) -> None:
        self._update_status(job, JobStatus.HIGHLIGHT_EXTRACTING)
        source_path = self._resolve_source_path(job)
        output_path = self.workspace_root / job.user_id / job.project_name / "generated" / "highlight" / f"{Path(source_path).stem}_highlight.mp4"
        self.catcut_service.extract_highlight(str(source_path), str(output_path))
        job.metadata["highlight_path"] = str(output_path)
        self._update_status(job, JobStatus.COMPLETED)

    def _process_shorts(self, job: Job) -> None:
        self._update_status(job, JobStatus.RENDERING)
        source_path = self._resolve_source_path(job)
        output_path = self.workspace_root / job.user_id / job.project_name / "generated" / "shorts" / f"{Path(source_path).stem}_shorts.mp4"
        self.catcut_service.create_shorts(str(source_path), str(output_path))
        job.metadata["shorts_path"] = str(output_path)
        self._update_status(job, JobStatus.COMPLETED)

    def _process_thumbnail(self, job: Job) -> None:
        self._update_status(job, JobStatus.RENDERING)
        source_path = self._resolve_source_path(job)
        output_path = self.workspace_root / job.user_id / job.project_name / "generated" / "thumbnail" / f"{Path(source_path).stem}_thumbnail.jpg"
        self.catcut_service.create_thumbnail(str(source_path), str(output_path))
        job.metadata["thumbnail_path"] = str(output_path)
        self._update_status(job, JobStatus.COMPLETED)

    def _process_export(self, job: Job) -> None:
        self._update_status(job, JobStatus.RENDERING)
        source_path = self._resolve_source_path(job)
        output_dir = (
            self.workspace_root
            / job.user_id
            / job.project_name
            / "generated"
            / "longform"
        )
        subtitle_payload = None
        subtitle_path = (
            self.workspace_root
            / job.user_id
            / job.project_name
            / "generated"
            / "subtitle"
            / f'{job.metadata["upload_id"]}.json'
        )
        if subtitle_path.is_file():
            with subtitle_path.open("r", encoding="utf-8") as file:
                subtitle_payload = json.load(file)
        result = self.export_service.render(
            source_path,
            output_dir,
            job.job_id,
            job.metadata,
            subtitle_payload,
        )
        job.metadata["export"] = result
        self._update_status(job, JobStatus.COMPLETED)

    def _resolve_source_path(self, job: Job) -> Path:
        file_path = job.metadata.get("path")
        if not file_path:
            raise ValueError("Job source path is missing")
        source_path = self.workspace_root / Path(file_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Source file does not exist: {source_path}")
        return source_path

    def _update_status(self, job: Job, status: JobStatus) -> None:
        job.status = status
        job.updated_at = datetime.now()
        self.repository.update(job)

    def _mark_job_failed(self, job: Job, message: str) -> None:
        job.status = JobStatus.FAILED
        job.metadata["error"] = message
        job.updated_at = datetime.now()
        self.repository.update(job)

    def _write_metadata(self, job: Job, payload: dict) -> Path:
        metadata_dir = self.workspace_root / job.user_id / job.project_name / "metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        output_file = metadata_dir / f"{job.job_id}_{job.job_type.value.lower()}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        return output_file

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
