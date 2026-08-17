from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from auth import get_current_user
router=APIRouter(
    prefix="/task",
    tags=["Tasks"]
)

tasks = []


class TaskRequest(BaseModel):
    title: str
    description: str


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


def check_ownership(task_id: str, user_id):
    for task in tasks:
        if (
            task["task_id"] == task_id
            and task["user_id"] == str(user_id)
        ):
            return task

    raise HTTPException(
        status_code=404,
        detail="Task not found"
    )



@router.post("/create_task")
def create_task(
    request: TaskRequest,
    current_user=Depends(get_current_user)
):
    task = {
        "task_id": str(uuid4()),
        "title": request.title,
        "description": request.description,
        "user_id": str(current_user["user_id"])
    }

    tasks.append(task)

    return {
        "message": "Task successfully created",
        "task": task
    }


@router.get("/all_tasks")
def all_tasks(
    current_user=Depends(get_current_user)
):
    user_id = str(current_user["user_id"])

    user_tasks = [
        task
        for task in tasks
        if task["user_id"] == user_id
    ]

    return {
        "user_id": user_id,
        "tasks": user_tasks
    }


@router.get("/{task_id}")
def task_get(
    task_id: str,
    current_user=Depends(get_current_user)
):
    task = check_ownership(
        task_id,
        current_user["user_id"]
    )

    return {
        "task": task
    }


@router.patch("/{task_id}")
def update_task(
    task_id: str,
    task_update: TaskUpdate,
    current_user=Depends(get_current_user)
):
    task = check_ownership(
        task_id,
        current_user["user_id"]
    )

    if task_update.title is None and task_update.description is None:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )

    if task_update.title is not None:
        task["title"] = task_update.title

    if task_update.description is not None:
        task["description"] = task_update.description

    return {
        "message": "Task updated successfully",
        "task": task
    }


@router.delete("/delete/{task_id}")
def delete_task(
    task_id: str,
    current_user=Depends(get_current_user)
):
    task = check_ownership(
        task_id,
        current_user["user_id"]
    )

    tasks.remove(task)

    return {
        "message": "Task deleted successfully",
        "task_id": task_id
    }