from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from typing import Optional
from data_operator import (
    validate_file_type,
    fhe_encrypt,
    delete_file,
    ENCRYPTED_DIRECTORY,
)
import string
import random
import asyncio
import os
from data_operator.zerog.operator import ZeroGOperator

file_router = APIRouter(prefix="/file")

UPLOAD_DIRECTORY = "./uploads"

zerog_operator = ZeroGOperator("http://3.87.11.89:5678")


@file_router.post("")
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
        "".join(random.choice(string.ascii_letters) for _ in range(5))
        + "-"
        + file.filename
    )
    if os.path.exists(f"{UPLOAD_DIRECTORY}/{file_name}"):
        raise HTTPException(
            status_code=409,
            detail="File already exists, please try again with a different file.",
        )
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)
    with open(f"{UPLOAD_DIRECTORY}/{file_name}", "wb") as f:
        f.write(contents)
    fhe_task = asyncio.create_task(fhe_encrypt(UPLOAD_DIRECTORY, file_name))
    if chain_option == "0G":
        asyncio.create_task(zerog_operator.register_file(fhe_task))
    return {"message": "File uploaded successfully", "file_name": file_name}


@file_router.get("/{file_name}")
async def get_file(file_name: str):
    if file_name.endswith(".zip") is not True:
        file_name = f"{''.join(file_name.split('.')[:-1])}.zip"
    file_path = f"{ENCRYPTED_DIRECTORY}/encrypted-{file_name}"
    print(file_path)
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="File not found, if you have uploaded the file, please wait for the encryption to complete.",
        )
    # asyncio.create_task(delete_file(file_name))
    return FileResponse(file_path)
