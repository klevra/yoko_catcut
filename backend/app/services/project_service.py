from pathlib import Path
from app.models.models import Project
from app.repositories.project_repository import ProjectRepository
from datetime import datetime
from app.core.config import get_settings


class ProjectService:
    """프로젝트 관리 서비스"""

    def __init__(self):
        settings = get_settings()
        self.workspace_root = Path(settings.workspace_root)
        self.repository = ProjectRepository()

    def create_project(self, user_id: str, project_name: str) -> dict:
        """프로젝트 생성"""
        # 프로젝트 경로 생성
        project_path = self.workspace_root / user_id / project_name
        project_path.mkdir(parents=True, exist_ok=True)

        # 서브 디렉토리 생성
        (project_path / "original").mkdir(exist_ok=True)
        (project_path / "generated").mkdir(exist_ok=True)
        (project_path / "generated" / "subtitle").mkdir(exist_ok=True)
        (project_path / "generated" / "shorts").mkdir(exist_ok=True)
        (project_path / "generated" / "longform").mkdir(exist_ok=True)
        (project_path / "generated" / "thumbnail").mkdir(exist_ok=True)
        (project_path / "generated" / "highlight").mkdir(exist_ok=True)
        (project_path / "metadata").mkdir(exist_ok=True)
        (project_path / "jobs").mkdir(exist_ok=True)

        # 프로젝트 저장
        project = Project(
            user_id=user_id,
            project_name=project_name,
            path=str(project_path),
        )
        self.repository.create(project)

        return {
            "user_id": user_id,
            "project_name": project_name,
            "path": str(project_path),
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat(),
        }

    def list_projects(self, user_id: str) -> list:
        """사용자의 프로젝트 목록 조회"""
        projects = self.repository.list_by_user(user_id)
        return [
            {
                "user_id": p.user_id,
                "project_name": p.project_name,
                "path": p.path,
                "created_at": p.created_at.isoformat(),
                "updated_at": p.updated_at.isoformat(),
            }
            for p in projects
        ]

    def get_project(self, user_id: str, project_name: str) -> dict:
        """프로젝트 상세 조회"""
        project = self.repository.read(user_id, project_name)
        if not project:
            raise ValueError(f"Project not found: {project_name}")
        return {
            "user_id": project.user_id,
            "project_name": project.project_name,
            "path": project.path,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat(),
        }

    def update_project(self, user_id: str, project_name: str, new_name: str) -> dict:
        """프로젝트 이름 변경"""
        project = self.repository.read(user_id, project_name)
        if not project:
            raise ValueError(f"Project not found: {project_name}")

        # 기존 디렉토리 변경
        old_path = Path(project.path)
        new_path = old_path.parent / new_name
        old_path.rename(new_path)

        # 프로젝트 정보 업데이트
        project.project_name = new_name
        project.path = str(new_path)
        project.updated_at = datetime.now()

        self.repository.update(project)

        # 기존 프로젝트 삭제
        self.repository.delete(user_id, project_name)
        self.repository.create(project)

        return {
            "user_id": project.user_id,
            "project_name": project.project_name,
            "path": project.path,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat(),
        }

    def delete_project(self, user_id: str, project_name: str) -> bool:
        """프로젝트 삭제"""
        project = self.repository.read(user_id, project_name)
        if not project:
            raise ValueError(f"Project not found: {project_name}")

        # 디렉토리 삭제
        import shutil

        project_path = Path(project.path)
        if project_path.exists():
            shutil.rmtree(project_path)

        # 저장소에서 삭제
        return self.repository.delete(user_id, project_name)
