from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path
import os
import gzip
import shutil
from binance.client import Client

app = FastAPI()

base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
grandparent_dir = os.path.dirname(parent_dir)
files_dir = os.path.join(grandparent_dir, "binance/Trade-Bot/core/files")

logs_dir = os.path.join(grandparent_dir, "binance/Trade-Bot/logs")
api_key = 'iyJXPaZztWrimkH6V57RGvStFgYQWRaaMdaYBQHHIEv0mMY1huCmrzTbXkaBjLFh'
api_secret = 'hmrus7zI9PW2EXqsDVovoS2cEFRVsxeETGgBf4XJInOLFcmIXKNL23alGRNRbXKI'


def compress_file(input_file, output_file):
    with open(input_file, 'rb') as f_in, gzip.open(output_file, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)


@app.get("/get_trade_statement")
async def get_statement():
    # Path to the file you want to return
    file_path = Path(f"{files_dir}/model_dataset.csv")  # Replace with the actual file path

    # Optional: Specify the desired file name for the response
    file_name = "statement_report.csv"

    # Return the file as a response
    return FileResponse(file_path, filename=file_name)


@app.get("/get_trade_logs")
async def get_logs():
    file_path = Path(f"{logs_dir}/binance_logs.log")  # Replace with the actual file path
    file_name = "trade_logs.txt"

    compress_file(file_path, file_name)

    # Path to the file you want to return

    # Optional: Specify the desired file name for the response

    # Return the file as a response
    return FileResponse(file_path, filename=file_name)


@app.get('/get_wallet')
def get_wallet():
    binance_wallet = []
    client = Client(api_key, api_secret)
    futures_account_info = client.futures_account()
    for asset in futures_account_info['assets']:
        asset_name = asset['asset']
        wallet_balance = asset['walletBalance']
        print(f'{asset_name} - Wallet Balance: {wallet_balance}')
        binance_dict = {
            'Asset': f'{asset_name} - Wallet Balance: {wallet_balance}'
        }
        binance_wallet.append(binance_dict)
    return binance_wallet


