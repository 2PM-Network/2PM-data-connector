from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from typing import Optional
from data_operator import (
    validate_file_type,
    fhe_encrypt,
    upload_file_to_0g,
    delete_file,
    ENCRYPTED_DIRECTORY,
)
import string
import random
import asyncio
import os

file_router = APIRouter(prefix="/file")

UPLOAD_DIRECTORY = "./uploads"


@file_router.post("", status_code=201)
async def upload_file(
    file: UploadFile = File(...), chain_option: Optional[str] = Form("0G")
):
    if not validate_file_type(file.filename):
        raise HTTPException(status_code=403, detail="Invalid file type")

    if chain_option not in ["0G", "IPFS"]:
        raise HTTPException(status_code=403, detail="Invalid chain option")

    contents = await file.read()
    # random file-name
    file_name = (
        "".join(random.choice(string.ascii_letters) for _ in range(5)) + file.filename
    )
    with open(f"{UPLOAD_DIRECTORY}/{file_name}", "wb") as f:
        f.write(contents)
    fhe_task = asyncio.create_task(fhe_encrypt(UPLOAD_DIRECTORY, file_name))
    if chain_option == "0G":
        asyncio.create_task(upload_file_to_0g(fhe_task))
    return {"message": "File uploaded successfully", "file_name": file_name}


@file_router.get("{file_name}")
async def get_file(file_name: str):
    file_path = f"{ENCRYPTED_DIRECTORY}/encrypted-{file_name}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    asyncio.create_task(delete_file(file_name))
    return FileResponse(file_path)
