from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import Task


router = APIRouter(
    prefix="/task",
    tags=["Tasks"]
)


class TaskRequest(BaseModel):
    title: str
    description: str


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


def check_ownership(
    task_id: str,
    user_id: str,
    db: Session
):
    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.user_id == user_id
        )
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


@router.post("/create_task")
def create_task(
    request: TaskRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = str(current_user.id)

    task_exists = (
        db.query(Task)
        .filter(
            Task.title == request.title,
            Task.description == request.description,
            Task.user_id == user_id
        )
        .first()
    )

    if task_exists:
        raise HTTPException(
            status_code=409,
            detail="Task already exists"
        )

    task = Task(
        id=str(uuid4()),
        title=request.title,
        description=request.description,
        user_id=user_id
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "message": "Task successfully created",
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "user_id": task.user_id
        }
    }


@router.get("/all_tasks")
def all_tasks(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = str(current_user.id)

    user_tasks = (
        db.query(Task)
        .filter(Task.user_id == user_id)
        .all()
    )

    return {
        "user_id": user_id,
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "user_id": task.user_id
            }
            for task in user_tasks
        ]
    }


@router.get("/{task_id}")
def task_get(
    task_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = str(current_user.id)

    task = check_ownership(
        task_id,
        user_id,
        db
    )

    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "user_id": task.user_id
    }


@router.patch("/{task_id}")
def update_task(
    task_id: str,
    task_update: TaskUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = str(current_user.id)

    task = check_ownership(
        task_id,
        user_id,
        db
    )

    if (
        task_update.title is None
        and task_update.description is None
    ):
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )

    if task_update.title is not None:
        task.title = task_update.title

    if task_update.description is not None:
        task.description = task_update.description

    db.commit()
    db.refresh(task)

    return {
        "message": "Task updated successfully",
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "user_id": task.user_id
        }
    }


@router.delete("/delete/{task_id}")
def delete_task(
    task_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = str(current_user.id)

    task = check_ownership(
        task_id,
        user_id,
        db
    )

    db.delete(task)
    db.commit()

    return {
        "message": "Task deleted successfully",
        "task_id": task_id
    }