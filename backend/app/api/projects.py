from fastapi import APIRouter, HTTPException
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from app.api.deps import current_user
from app.services.project_service import ProjectService
from fastapi import Depends

router = APIRouter()
service = ProjectService()


@router.post("", response_model=dict)
def create_project(payload: ProjectCreate, user_id: str = Depends(current_user)):
    """프로젝트 생성"""
    try:
        if payload.user_id != user_id:
            raise ValueError("You can only create your own projects")
        return service.create_project(payload.user_id, payload.project_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}")
def list_projects(user_id: str, authenticated: str = Depends(current_user)):
    """사용자의 프로젝트 목록 조회"""
    try:
        if user_id != authenticated:
            raise ValueError("You can only list your own projects")
        return service.list_projects(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}/{project_name}")
def get_project(
    user_id: str,
    project_name: str,
    authenticated: str = Depends(current_user),
):
    """프로젝트 상세 조회"""
    try:
        if user_id != authenticated:
            raise ValueError("You can only access your own projects")
        return service.get_project(user_id, project_name)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{user_id}/{project_name}")
def update_project(
    user_id: str,
    project_name: str,
    payload: ProjectUpdate,
    authenticated: str = Depends(current_user),
):
    """프로젝트 정보 수정"""
    try:
        if payload.project_name:
            return service.update_project(user_id, project_name, payload.project_name)
        return service.get_project(user_id, project_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}/{project_name}")
def delete_project(
    user_id: str,
    project_name: str,
    authenticated: str = Depends(current_user),
):
    """프로젝트 삭제"""
    try:
        success = service.delete_project(user_id, project_name)
        return {"success": success, "message": "Project deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        if user_id != authenticated:
            raise ValueError("You can only update your own projects")
        if user_id != authenticated:
            raise ValueError("You can only delete your own projects")
