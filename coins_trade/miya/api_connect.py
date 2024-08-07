import requests


def get_trade_settings(symbol):

    url = 'http://77.37.51.134:8080/get_trade_setting/'

    # Send a GET request with the symbol as a query parameter
    response = requests.get(url, headers={'accept': 'application/json'}, params={'symbol': symbol})

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        
        # Filter the data for the specific symbol
        filtered_data = [item for item in data if item['symbol'] == symbol]
        
        print(filtered_data[0])
        return filtered_data[0]
    else:
        print(f"Failed to retrieve data: {response.status_code}")


if __name__ == '__main__':
    symbol = 'BTCUSDT'

    get_trade_settings(symbol=symbol)