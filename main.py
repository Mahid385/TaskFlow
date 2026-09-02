import logging

from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from auth import router as auth_router
from task import router as task_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger=logging.getLogger(__name__)

app = FastAPI(
    title="TaskFlow API",
    version="1.0.0"
)

@app.exception_handler(Exception)
async def global_exception_handler(
    request:Request,
    exc:Exception
):
    logger.error(
        "Unhandled exception: %s %s",
        request.method,
        request.url.path,
        exc_info=exc
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error"
        }
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(task_router)

if __name__=="__main__":
    uvicorn.run("main:app",reload=True,host="127.0.0.1",port=8000)