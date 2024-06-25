import warnings

warnings.simplefilter(action='ignore')

import pandas as pd
import ccxt.async_support as ccxt
import numpy as np
import asyncio
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from gym import Env
from gym.spaces import Discrete, Box


# Fetch OHLCV data
async def fetch_ohlcv(symbol='MATIC/USDT', timeframe='15m', limit=100):
    exchange = ccxt.binance()
    ohlcv = await exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    await exchange.close()
    return df


# Generate signals based on moving averages
def generate_signals(df):
    ma1 = 12
    ma2 = 26
    signals = df.copy()
    signals['ma1'] = signals['close'].rolling(window=ma1, min_periods=1, center=False).mean()
    signals['ma2'] = signals['close'].rolling(window=ma2, min_periods=1, center=False).mean()
    signals['positions'] = 0
    signals['positions'][ma1:] = np.where(signals['ma1'][ma1:] >= signals['ma2'][ma1:], 1, 0)
    signals['signals'] = signals['positions'].diff()

    # Map numeric signals to string signals
    signal_map = {
        1.0: 'Buy',
        -1.0: 'Sell',
        0.0: 'Hold'
    }
    signals['signals'] = signals['signals'].map(signal_map)

    signals['oscillator'] = signals['ma1'] - signals['ma2']
    return signals


class TradingEnv(Env):
    def __init__(self, df):
        super(TradingEnv, self).__init__()
        self.df = df
        self.action_space = Discrete(3)  # Buy, Sell, Hold
        self.observation_space = Box(low=-np.inf, high=np.inf, shape=(6,), dtype=np.float32)
        self.current_step = 0
        self.initial_balance = 10000
        self.balance = self.initial_balance
        self.crypto_held = 0
        self.net_worth = self.initial_balance

    def reset(self):
        self.current_step = 0
        self.balance = self.initial_balance
        self.crypto_held = 0
        self.net_worth = self.initial_balance
        return self._next_observation()

    def _next_observation(self):
        obs = np.array([
            self.df.iloc[self.current_step]['open'],
            self.df.iloc[self.current_step]['high'],
            self.df.iloc[self.current_step]['low'],
            self.df.iloc[self.current_step]['close'],
            self.df.iloc[self.current_step]['volume'],
            self.df.iloc[self.current_step]['oscillator']
        ])
        return obs

    def step(self, action):
        current_price = self.df.iloc[self.current_step]['close']

        if action == 0:  # Buy
            self.crypto_held += self.balance / current_price
            self.balance = 0
        elif action == 1:  # Sell
            self.balance += self.crypto_held * current_price
            self.crypto_held = 0

        self.current_step += 1
        self.net_worth = self.balance + self.crypto_held * current_price

        done = self.current_step >= len(self.df) - 1
        reward = self.net_worth - self.initial_balance

        obs = self._next_observation()
        return obs, reward, done, {}

    def render(self, mode='human'):
        profit = self.net_worth - self.initial_balance
        print(f'Step: {self.current_step}')
        print(f'Balance: {self.balance}')
        print(f'Crypto held: {self.crypto_held}')
        print(f'Net worth: {self.net_worth}')
        print(f'Profit: {profit}')


# Fetch data and generate signals
async def main():
    df = await fetch_ohlcv()
    signals = generate_signals(df)
    env = DummyVecEnv([lambda: TradingEnv(signals)])
    model = PPO('MlpPolicy', env, verbose=1)
    model.learn(total_timesteps=10000)
    model.save("ppo_trading_model")


if __name__ == '__main__':
    asyncio.run(main())
