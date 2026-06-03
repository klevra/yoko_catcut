from pathlib import Path
from fastapi import UploadFile
from app.storage import LocalStorageAdapter
from app.core.config import get_settings
import uuid


class StorageService:
    """파일 스토리지 서비스"""

    def __init__(self):
        settings = get_settings()
        self.storage_adapter = LocalStorageAdapter(settings.workspace_root)
        self.max_file_size = settings.max_file_size_gb * 1024 * 1024 * 1024

    async def save_original(
        self, user_id: str, project_name: str, file: UploadFile
    ) -> dict:
        """원본 파일 저장"""
        # 파일 크기 검증
        contents = await file.read()
        if len(contents) > self.max_file_size:
            raise ValueError(
                f"File size exceeds maximum allowed size: {self.max_file_size}"
            )

        # 고유한 파일명 생성
        file_id = str(uuid.uuid4())
        _, ext = Path(file.filename).name.split(".")
        dest_filename = f"{file_id}.{ext}"
        dest_path = f"{user_id}/{project_name}/original/{dest_filename}"

        # 임시 파일 저장
        temp_path = Path("/tmp") / dest_filename
        with open(temp_path, "wb") as f:
            f.write(contents)

        # 스토리지에 저장
        saved_path = await self.storage_adapter.save_file(str(temp_path), dest_path)
        temp_path.unlink()

        return {
            "upload_id": file_id,
            "filename": file.filename,
            "path": dest_path,
            "file_size": len(contents),
        }

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
