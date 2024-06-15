import pandas as pd
from concrete.ml.pandas import ClientEngine
import os
import asyncio

client = ClientEngine(keys_path="2pm-key")

ENCRYPTED_DIRECTORY = "./encrypted"


def validate_file_type(file_name: str):
    # in csv, xlsx, xls, json,
    return file_name.split(".")[-1] in ["csv", "xlsx", "xls", "json"]


async def convert_file_to_df(file_name: str, contents: bytes):
    if file_name.split(".")[-1] == "csv":
        return pd.read_csv(contents)
    elif file_name.split(".")[-1] == "xlsx" or file_name.split(".")[-1] == "xls":
        return pd.read_excel(contents)
    elif file_name.split(".")[-1] == "json":
        return pd.read_json(contents)
    else:
        raise ValueError("Invalid file type")


async def fhe_encrypt(file_path: str, file_name: str):
    with open(f"{file_path}/{file_name}", "r") as f:
        data = f.read()
    df = convert_file_to_df(file_name, data)
    df_entrypted = client.encrypt_from_pandas(df)
    df_entrypted.save(f"{ENCRYPTED_DIRECTORY}/encrypted-{file_name}")
    return f"{ENCRYPTED_DIRECTORY}/encrypted-{file_name}"


async def delete_file(file_name: str):
    asyncio.sleep(600)
    os.remove(f"{ENCRYPTED_DIRECTORY}/encrypted-{file_name}")
