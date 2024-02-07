from binance.client import Client

api_key = 'iyJXPaZztWrimkH6V57RGvStFgYQWRaaMdaYBQHHIEv0mMY1huCmrzTbXkaBjLFh'
api_secret = 'hmrus7zI9PW2EXqsDVovoS2cEFRVsxeETGgBf4XJInOLFcmIXKNL23alGRNRbXKI'


def get_position_history():
    client = Client(api_key, api_secret)
    data = client.futures_account_trades()
    return data


if __name__ == '__main__':
    res = get_position_history()
    print(res)
