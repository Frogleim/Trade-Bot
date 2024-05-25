from fastapi import FastAPI, HTTPException, Response, File
from typing import Annotated

app = FastAPI()


@app.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}
