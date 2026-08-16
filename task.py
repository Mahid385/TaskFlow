from fastapi import FastAPI,Depends,HTTPException
from pydantic import BaseModel
from auth import get_current_user
from uuid import uuid4
app=FastAPI()

tasks=[]
class TaskRequest(BaseModel):
    title:str
    description:str

class TaskUpdate(BaseModel):
    title:str|None
    description:str|None


def find_user_tasks(current_user):
    user_tasks=[
        task for task in tasks
        if task["user_id"]==current_user["user_id"]
    ] 
    return user_tasks

@app.post("/task/create_task")
def create_task(request:TaskRequest,current_user=Depends(get_current_user)):
    task_id=uuid4()
    
    user_id=current_user["user_id"]
    task={
        "user_id":user_id,
        "task_id":str(task_id),
        "title":request.title,
        "description":request.description
    }
    tasks.append(task)
    return {
        "user_id":current_user["user_id"],
        "task_id":task_id,
        "message":"task successfully created"
    }

@app.get("/task/all_tasks")
def all_tasks(current_user=Depends(get_current_user)):
    try:
        user_id=current_user.get("user_id")
        user_tasks=find_user_tasks(current_user)
        return {
            "user_id":user_id,
            "all_tasks":user_tasks
        }
    except:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )
@app.get("/task/{task_id}")
def task_get(task_id:str,current_user=Depends(get_current_user)):
    user_id=current_user.get("user_id")
    user_tasks=find_user_tasks(current_user)
    for task in user_tasks:
        if task["task_id"]==task_id:
            return {
                "user_id":str(user_id),
                "task_id":task_id,
                "task":task
            }
    
    return{
        "user_id":str(user_id),
        "message":f"No task with this task id {task_id} found"
    }

@app.patch("/task/{task_id}")
def update_task(task_id:str,task_update:TaskUpdate,current_user=Depends(get_current_user)):
    user_tasks=find_user_tasks(current_user)
    user_task_update={}
    for task in user_tasks:
        if task["task_id"]==task_id:

            if task_update.title:
                task["title"]=task_update.title
            elif task_update.description:
                task["description"]=task_update.description
            elif task_update.title and task_update.description:
                task["title"]=task_update.title
                task["description"]=task_update.description

            else:
                raise HTTPException(
                    status_code=401,
                    detail="Task Update endpoint is empty"
                )
            user_task_update=task
    for inst in tasks:
        if inst["task_id"]==task_id:
            inst=user_task_update

    return {
        "user_id":current_user["user_id"],
        "task_id":task_id,
        "message":"task update successfuly"
    }

@app.delete("/task/delete/{task_id}")
def delete_task(task_id:str,current_user=Depends(get_current_user)):
    if find_user_tasks(current_user):
        for task in tasks:
            if task["task_id"]==task_id:
                task.remove()
                return{
                    "user_id":current_user["user_id"],
                    "task_id":task_id,
                    "message":"deleted successfully"
                }
    else:
        raise HTTPException(
            status_code=401,
            detail="task not found"
        )