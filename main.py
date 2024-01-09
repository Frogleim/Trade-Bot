from fastapi import FastAPI, Query
import os
import gzip
import shutil
from binance.client import Client
import core.trade.ETH.config
from binance_api import api

app = FastAPI()

base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
grandparent_dir = os.path.dirname(parent_dir)
files_dir = os.path.join(grandparent_dir, "bot/Trade-Bot/core/trade/files")

logs_dir = os.path.join(grandparent_dir, "binance/Trade-Bot/trade/logs")
api_key = 'iyJXPaZztWrimkH6V57RGvStFgYQWRaaMdaYBQHHIEv0mMY1huCmrzTbXkaBjLFh'
api_secret = 'hmrus7zI9PW2EXqsDVovoS2cEFRVsxeETGgBf4XJInOLFcmIXKNL23alGRNRbXKI'


def compress_file(input_file, output_file):
    with open(input_file, 'rb') as f_in, gzip.open(output_file, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)


@app.get('/get_wallet')
def get_wallet():
    binance_wallet = []
    client = Client(api_key, api_secret)
    futures_account_info = client.futures_account()
    for asset in futures_account_info['assets']:
        asset_name = asset['asset']
        wallet_balance = round(float(asset['walletBalance']), 2)
        print(f'{asset_name} - Wallet Balance: {wallet_balance}')
        binance_dict = {
            'Asset': f'{asset_name} - Wallet Balance: {wallet_balance}'
        }
        binance_wallet.append(binance_dict)
    return binance_wallet


@app.get('/current_position')
def get_positions():
    client = Client(api_key, api_secret)
    position_info = client.futures_position_information(symbol=core.trade.ETH.config.trading_pair)
    return position_info


@app.get('/position_alert')
def position_alert():
    new_position = api.get_position_history()
    return new_position
