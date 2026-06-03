from pathlib import Path
from fastapi import UploadFile

from app.core.config import get_settings


class StorageAdapter:
    async def save_original(self, user_id: str, project_name: str, file: UploadFile) -> str:
        raise NotImplementedError


class LocalStorageAdapter(StorageAdapter):
    def __init__(self):
        self.settings = get_settings()

    async def save_original(self, user_id: str, project_name: str, file: UploadFile) -> str:
        original_dir = Path(self.settings.workspace_root) / user_id / project_name / "original"
        original_dir.mkdir(parents=True, exist_ok=True)

        target = original_dir / file.filename
        content = await file.read()
        target.write_bytes(content)
        return str(target)


class NasStorageAdapter(StorageAdapter):
    async def save_original(self, user_id: str, project_name: str, file: UploadFile) -> str:
        # TODO: SMB/NFS adapter 구현
        raise NotImplementedError("NAS storage adapter is not implemented yet.")


class StorageService:
    def __init__(self):
        settings = get_settings()
        if settings.storage_type == "nas":
            self.adapter = NasStorageAdapter()
        else:
            self.adapter = LocalStorageAdapter()

    async def save_original(self, user_id: str, project_name: str, file: UploadFile) -> str:
        return await self.adapter.save_original(user_id, project_name, file)
