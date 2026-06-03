from pathlib import Path
from app.core.config import get_settings


class ProjectService:
    def __init__(self):
        self.settings = get_settings()

    def create_project(self, user_id: str, project_name: str) -> dict:
        root = Path(self.settings.workspace_root)
        project = root / user_id / project_name

        for folder in [
            project / "original",
            project / "generated" / "subtitle",
            project / "generated" / "shorts",
            project / "generated" / "longform",
            project / "generated" / "thumbnail",
            project / "generated" / "highlight",
            project / "metadata",
            project / "jobs",
        ]:
            folder.mkdir(parents=True, exist_ok=True)

        return {
            "user_id": user_id,
            "project_name": project_name,
            "path": str(project),
        }

    def list_projects(self, user_id: str) -> list[dict]:
        user_root = Path(self.settings.workspace_root) / user_id
        if not user_root.exists():
            return []
        return [
            {
                "user_id": user_id,
                "project_name": p.name,
                "path": str(p),
            }
            for p in user_root.iterdir()
            if p.is_dir()
        ]
