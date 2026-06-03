from pydantic import BaseModel


class ProjectCreate(BaseModel):
    user_id: str
    project_name: str


class ProjectResponse(BaseModel):
    user_id: str
    project_name: str
    path: str
