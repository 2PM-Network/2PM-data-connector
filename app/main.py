from fastapi import FastAPI
from app.v1.file import file_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 可以改为你的允许的域名列表
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(file_router, prefix="/v1")
