import pandas as pd

def calculate_obv(data):
    obv = [0]
    for i in range(1, len(data)):
        if data['close'][i] > data['close'][i-1]:
            obv.append(obv[-1] + data['volume'][i])
        elif data['close'][i] < data['close'][i-1]:
            obv.append(obv[-1] - data['volume'][i])
        else:
            obv.append(obv[-1])
    data['OBV'] = obv
    return data

data = pd.read_csv('./models/data/MATICUSDT_historical.csv')

data = calculate_obv(data)
print(data[['close', 'volume', 'OBV']])
