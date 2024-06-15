from fastapi import FastAPI
from v1.file import file_router

app = FastAPI()

app.include_router(file_router, prefix="/v1")
