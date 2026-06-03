from typing import List, Optional
from app.models.models import Project
import json
from pathlib import Path


class ProjectRepository:
    """Project 데이터 영속성 관리"""

    def __init__(self, storage_path: str = "./data/projects"):
        self.storage_path = Path(storage_path)
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
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        return project

    def read(self, user_id: str, project_name: str) -> Optional[Project]:
        """프로젝트 조회"""
        file_path = self._get_project_file(user_id, project_name)
        if not file_path.exists():
            return None
        with open(file_path, "r") as f:
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
        if not user_dir.exists():
            return []
        projects = []
        for file in user_dir.glob("*.json"):
            with open(file, "r") as f:
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
