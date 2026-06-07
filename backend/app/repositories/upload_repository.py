import json
from pathlib import Path
from typing import List, Optional

from app.core.config import get_settings


class UploadRepository:
    """Workspace-backed upload metadata persistence."""

    def __init__(self, workspace_root: Optional[str] = None):
        root = workspace_root or get_settings().workspace_root
        self.workspace_root = Path(root)

    def _upload_dir(self, user_id: str, project_name: str) -> Path:
        return (
            self.workspace_root
            / user_id
            / project_name
            / "metadata"
            / "uploads"
        )

    def create(self, upload: dict) -> dict:
        upload_dir = self._upload_dir(upload["user_id"], upload["project_name"])
        upload_dir.mkdir(parents=True, exist_ok=True)
        target = upload_dir / f'{upload["upload_id"]}.json'
        temporary = target.with_suffix(".tmp")
        with temporary.open("w", encoding="utf-8") as file:
            json.dump(upload, file, indent=2, ensure_ascii=False)
        temporary.replace(target)
        return upload

    def read(self, upload_id: str) -> Optional[dict]:
        for target in self.workspace_root.glob(
            f"*/*/metadata/uploads/{upload_id}.json"
        ):
            with target.open("r", encoding="utf-8") as file:
                return json.load(file)
        return None

    def list_by_project(self, user_id: str, project_name: str) -> List[dict]:
        uploads = []
        upload_dir = self._upload_dir(user_id, project_name)
        if not upload_dir.is_dir():
            return uploads

        for target in upload_dir.glob("*.json"):
            with target.open("r", encoding="utf-8") as file:
                uploads.append(json.load(file))
        return sorted(
            uploads,
            key=lambda upload: upload.get("created_at", ""),
            reverse=True,
        )
