from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path
import os

app = FastAPI()

base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
files_dir = os.path.join(parent_dir, "Trade-Bot\\core\\files")
print(files_dir)
@app.get("/get-statement")
async def get_statement():
    file_path = Path(f"{files_dir}/model_dataset.csv")  # Replace with the actual file path
    file_name = "statement.csv"
    return FileResponse(file_path, filename=file_name)
