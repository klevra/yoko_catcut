from typing import List, Optional
from app.models.models import Project
import json
from datetime import datetime
from pathlib import Path
from app.core.config import get_settings


class ProjectRepository:
    """Project 데이터 영속성 관리"""

    def __init__(self, storage_path: str = None):
        self.workspace_root = Path(get_settings().workspace_root)
        self.storage_path = Path(
            storage_path
            or self.workspace_root / ".system" / "projects"
        )
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _get_project_file(self, user_id: str, project_name: str) -> Path:
        user_dir = self.storage_path / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir / f"{project_name}.json"

    def create(self, project: Project) -> Project:
        """프로젝트 생성"""
        file_path = self._get_project_file(project.user_id, project.project_name)
        data = {
            "user_id": project.user_id,
            "project_name": project.project_name,
            "path": project.path,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat(),
        }
        temporary = file_path.with_suffix(".tmp")
        with open(temporary, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        temporary.replace(file_path)
        return project

    def read(self, user_id: str, project_name: str) -> Optional[Project]:
        """프로젝트 조회"""
        file_path = self._get_project_file(user_id, project_name)
        if not file_path.exists():
            project_path = self.workspace_root / user_id / project_name
            if not project_path.is_dir():
                return None
            project = self._project_from_directory(user_id, project_path)
            self.create(project)
            return project
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Project(
            user_id=data["user_id"],
            project_name=data["project_name"],
            path=data["path"],
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def list_by_user(self, user_id: str) -> List[Project]:
        """사용자의 모든 프로젝트 조회"""
        user_dir = self.storage_path / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        workspace_user_dir = self.workspace_root / user_id
        if workspace_user_dir.is_dir():
            for project_path in workspace_user_dir.iterdir():
                if not project_path.is_dir() or project_path.name.startswith("."):
                    continue
                metadata_path = user_dir / f"{project_path.name}.json"
                if not metadata_path.exists():
                    self.create(
                        self._project_from_directory(user_id, project_path)
                    )

        projects = []
        for file in user_dir.glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
            projects.append(
                Project(
                    user_id=data["user_id"],
                    project_name=data["project_name"],
                    path=data["path"],
                    created_at=data.get("created_at"),
                    updated_at=data.get("updated_at"),
                )
            )
        return projects

    @staticmethod
    def _project_from_directory(user_id: str, project_path: Path) -> Project:
        created_at = datetime.fromtimestamp(project_path.stat().st_ctime)
        updated_at = datetime.fromtimestamp(project_path.stat().st_mtime)
        return Project(
            user_id=user_id,
            project_name=project_path.name,
            path=str(project_path),
            created_at=created_at,
            updated_at=updated_at,
        )

    def update(self, project: Project) -> Project:
        """프로젝트 업데이트"""
        return self.create(project)

    def delete(self, user_id: str, project_name: str) -> bool:
        """프로젝트 삭제"""
        file_path = self._get_project_file(user_id, project_name)
        if file_path.exists():
            file_path.unlink()
            return True
        return False
