from pydantic import BaseModel,ConfigDict


class TaskCreate(BaseModel):
    title: str
    description: str


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    user_id: str
    model_config=ConfigDict(from_attributes=True)

class TaskListResponse(BaseModel):
    user_id: str
    tasks: list[TaskResponse]
    model_config=ConfigDict(from_attributes=True)