from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import shutil
import zipfile
import os
from pydantic import BaseModel
import db

app = FastAPI()


class BinanceKeys(BaseModel):
    api_key: str
    api_secret: str


base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
grandparent_dir = os.path.dirname(parent_dir)
files_dir = os.path.join(grandparent_dir, r"Trade-Bot/coins_trade/logs")


@app.get("/download-logs/")
def download_logs():
    # Define the path to the logs directory and the output zip file
    logs_directory = '/coins_trade/logs'
    zip_filename = '/coins_trade/logs.zip'

    # Ensure the directory exists
    if not os.path.exists(files_dir):
        raise HTTPException(status_code=404, detail="Logs directory not found")

    # Create a zip file containing all files from the logs directory
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(logs_directory):
            for file in files:
                # Create a complete filepath of file in directory
                file_path = os.path.join(root, file)
                # Add file to zip
                zipf.write(file_path, arcname=os.path.relpath(file_path, logs_directory))

    # Check if zip file has been created successfully
    if not os.path.exists(zip_filename):
        raise HTTPException(status_code=500, detail="Failed to create zip file")

    # Provide the zipped file as a response
    return FileResponse(path=zip_filename, media_type='application/zip', filename='logs.zip')


@app.get('/get_trades_history/')
def get_history():
    return {"Message": "Success"}


@app.post('/set_credentials/')
def set_credentials(keys: BinanceKeys):
    if keys.api_key or keys.api_secret is None:
        raise HTTPException(status_code=500, detail="API Key and API secret is required")
    api_key = keys.api_key
    api_secret = keys.api_secret
    my_db = db.DataBase()
    my_db.insert_binance_keys(api_key=api_key, api_secret=api_secret)
    return {"Message": "API keys insert successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
