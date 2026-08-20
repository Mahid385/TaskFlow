from fastapi import FastAPI
import uvicorn
from auth import router as auth_router
from task import router as task_router
from database import Base,engine

Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="TaskFlow API",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(task_router)

if __name__=="__main__":
    uvicorn.run("main:app",reload=True,host="127.0.0.1",port=800)