from fastapi import APIRouter
from app.schemas.project import ProjectCreate, ProjectResponse
from app.services.project_service import ProjectService

router = APIRouter()
service = ProjectService()


@router.post("", response_model=ProjectResponse)
def create_project(payload: ProjectCreate):
    return service.create_project(payload.user_id, payload.project_name)


@router.get("/{user_id}")
def list_projects(user_id: str):
    return service.list_projects(user_id)
