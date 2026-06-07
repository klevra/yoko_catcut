from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import UploadFile

from app.core.config import get_settings
from app.repositories.upload_repository import UploadRepository
from app.services.ffmpeg_service import FfmpegService
from app.services.subtitle_service import SubtitleService
from app.storage import LocalStorageAdapter
import uuid


class StorageService:
    """파일 스토리지 서비스"""

    ALLOWED_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm"}
    ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".m4a", ".aac", ".wav", ".flac", ".ogg"}
    CHUNK_SIZE = 1024 * 1024

    def __init__(self):
        settings = get_settings()
        self.storage_adapter = LocalStorageAdapter(settings.workspace_root)
        self.upload_repository = UploadRepository(settings.workspace_root)
        self.ffmpeg_service = FfmpegService()
        self.subtitle_service = SubtitleService()
        self.max_file_size = settings.max_file_size_gb * 1024 * 1024 * 1024

    async def save_original(
        self, user_id: str, project_name: str, file: UploadFile
    ) -> dict:
        """원본 파일 저장"""
        self._validate_segment(user_id, "user_id")
        self._validate_segment(project_name, "project_name")
        original_name = Path(file.filename or "").name
        extension = Path(original_name).suffix.lower()
        if extension not in self.ALLOWED_EXTENSIONS:
            allowed = ", ".join(sorted(self.ALLOWED_EXTENSIONS))
            raise ValueError(f"Unsupported video extension. Allowed: {allowed}")

        file_id = str(uuid.uuid4())
        dest_filename = f"{file_id}{extension}"
        dest_path = f"{user_id}/{project_name}/original/{dest_filename}"
        project_path = (
            self.storage_adapter.base_path / user_id / project_name
        )
        if not project_path.is_dir():
            raise ValueError(f"Project does not exist: {project_name}")

        file_size = 0
        temp_path = None
        try:
            with NamedTemporaryFile(suffix=extension, delete=False) as temporary:
                temp_path = Path(temporary.name)
                while chunk := await file.read(self.CHUNK_SIZE):
                    file_size += len(chunk)
                    if file_size > self.max_file_size:
                        raise ValueError(
                            "File size exceeds maximum allowed size: "
                            f"{self.max_file_size} bytes"
                        )
                    temporary.write(chunk)

            metadata = self.ffmpeg_service.probe(str(temp_path))
            await self.storage_adapter.save_file(str(temp_path), dest_path)
        finally:
            if temp_path and temp_path.exists():
                temp_path.unlink()
            await file.close()

        upload = {
            "upload_id": file_id,
            "user_id": user_id,
            "project_name": project_name,
            "filename": original_name,
            "path": dest_path,
            "file_size": file_size,
            "duration": metadata["duration"],
            "metadata": metadata,
            "created_at": datetime.now().isoformat(),
        }
        return self.upload_repository.create(upload)

    async def delete_file(self, file_path: str) -> bool:
        """파일 삭제"""
        return await self.storage_adapter.delete_file(file_path)

    def get_file_info(self, file_path: str) -> dict:
        """파일 정보 조회"""
        exists = self.storage_adapter.exists(file_path)
        if not exists:
            raise FileNotFoundError(f"File not found: {file_path}")

        file_size = self.storage_adapter.get_file_size(file_path)
        return {
            "path": file_path,
            "file_size": file_size,
            "exists": True,
        }

    def get_upload(self, upload_id: str) -> dict:
        upload = self.upload_repository.read(upload_id)
        if upload is None:
            raise FileNotFoundError(f"Upload not found: {upload_id}")
        return upload

    def ensure_upload_owner(self, upload_id: str, user_id: str) -> dict:
        upload = self.get_upload(upload_id)
        if upload["user_id"] != user_id:
            raise ValueError("You can only access your own uploads")
        return upload

    def list_uploads(self, user_id: str, project_name: str) -> list:
        self._validate_segment(user_id, "user_id")
        self._validate_segment(project_name, "project_name")
        return self.upload_repository.list_by_project(user_id, project_name)

    async def save_background_music(self, upload_id: str, file: UploadFile) -> dict:
        upload = self.get_upload(upload_id)
        original_name = Path(file.filename or "").name
        extension = Path(original_name).suffix.lower()
        if extension not in self.ALLOWED_AUDIO_EXTENSIONS:
            allowed = ", ".join(sorted(self.ALLOWED_AUDIO_EXTENSIONS))
            raise ValueError(f"Unsupported audio extension. Allowed: {allowed}")

        music_dir = (
            self.storage_adapter.base_path
            / upload["user_id"]
            / upload["project_name"]
            / "generated"
            / "music"
        )
        music_dir.mkdir(parents=True, exist_ok=True)
        target = music_dir / f"{upload_id}{extension}"
        file_size = 0
        temp_path = None
        try:
            with NamedTemporaryFile(suffix=extension, delete=False) as temporary:
                temp_path = Path(temporary.name)
                while chunk := await file.read(self.CHUNK_SIZE):
                    file_size += len(chunk)
                    temporary.write(chunk)
            target.write_bytes(temp_path.read_bytes())
        finally:
            if temp_path and temp_path.exists():
                temp_path.unlink()
            await file.close()
        return {
            "upload_id": upload_id,
            "filename": original_name,
            "path": str(target),
            "file_size": file_size,
        }

    def get_background_music_path(self, upload_id: str) -> Path | None:
        upload = self.get_upload(upload_id)
        music_dir = (
            self.storage_adapter.base_path
            / upload["user_id"]
            / upload["project_name"]
            / "generated"
            / "music"
        )
        if not music_dir.is_dir():
            return None
        for extension in sorted(self.ALLOWED_AUDIO_EXTENSIONS):
            candidate = music_dir / f"{upload_id}{extension}"
            if candidate.is_file():
                return candidate
        return None

    def get_upload_path(self, upload_id: str) -> Path:
        upload = self.get_upload(upload_id)
        path = self.storage_adapter._get_full_path(upload["path"])
        if not path.is_file():
            raise FileNotFoundError(f"Upload file not found: {upload_id}")
        return path

    def get_subtitle(self, upload_id: str) -> dict:
        upload = self.get_upload(upload_id)
        target = (
            self.storage_adapter.base_path
            / upload["user_id"]
            / upload["project_name"]
            / "generated"
            / "subtitle"
            / f"{upload_id}.json"
        )
        if not target.is_file():
            raise FileNotFoundError(f"Subtitle not found: {upload_id}")
        import json

        with target.open("r", encoding="utf-8") as file:
            return json.load(file)

    def get_subtitle_path(self, upload_id: str, file_format: str) -> Path:
        if file_format not in {"srt", "vtt", "json"}:
            raise ValueError("Unsupported subtitle format")
        upload = self.get_upload(upload_id)
        target = (
            self.storage_adapter.base_path
            / upload["user_id"]
            / upload["project_name"]
            / "generated"
            / "subtitle"
            / f"{upload_id}.{file_format}"
        )
        if not target.is_file():
            raise FileNotFoundError(f"Subtitle not found: {upload_id}")
        return target

    def save_subtitle(self, upload_id: str, segments: list) -> dict:
        upload = self.get_upload(upload_id)
        output_dir = (
            self.storage_adapter.base_path
            / upload["user_id"]
            / upload["project_name"]
            / "generated"
            / "subtitle"
        )
        current = self.get_subtitle(upload_id)
        current["segments"] = segments
        return self.subtitle_service.save(output_dir, upload_id, current)

    def get_speech_analysis(self, upload_id: str) -> dict:
        upload = self.get_upload(upload_id)
        target = (
            self.storage_adapter.base_path
            / upload["user_id"]
            / upload["project_name"]
            / "generated"
            / "subtitle"
            / f"{upload_id}_analysis.json"
        )
        if not target.is_file():
            raise FileNotFoundError(f"Speech analysis not found: {upload_id}")
        import json

        with target.open("r", encoding="utf-8") as file:
            return json.load(file)

    def get_speaker_preview_path(
        self,
        upload_id: str,
        speaker_id: str,
    ) -> Path:
        self._validate_segment(speaker_id, "speaker_id")
        upload = self.get_upload(upload_id)
        target = (
            self.storage_adapter.base_path
            / upload["user_id"]
            / upload["project_name"]
            / "generated"
            / "subtitle"
            / f"{upload_id}_{speaker_id}.mp3"
        )
        if not target.is_file():
            raise FileNotFoundError(f"Speaker preview not found: {speaker_id}")
        return target

    def get_export_path(self, upload_id: str, export_id: str) -> Path:
        upload = self.get_upload(upload_id)
        target = (
            self.storage_adapter.base_path
            / upload["user_id"]
            / upload["project_name"]
            / "generated"
            / "longform"
            / f"{export_id}.mp4"
        )
        if not target.is_file():
            raise FileNotFoundError(f"Export not found: {export_id}")
        return target

    def get_capcut_package_path(self, upload_id: str, export_id: str) -> Path:
        upload = self.get_upload(upload_id)
        target = (
            self.storage_adapter.base_path
            / upload["user_id"]
            / upload["project_name"]
            / "generated"
            / "longform"
            / f"{export_id}_capcut.zip"
        )
        if not target.is_file():
            raise FileNotFoundError(f"CapCut package not found: {export_id}")
        return target

    @staticmethod
    def _validate_segment(value: str, field_name: str) -> None:
        if (
            not value
            or value in {".", ".."}
            or "/" in value
            or "\\" in value
            or Path(value).name != value
        ):
            raise ValueError(f"Invalid {field_name}")
