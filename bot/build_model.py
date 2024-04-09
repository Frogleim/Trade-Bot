import numpy as np
import random
import ccxt
import pandas as pd
import pickle

# Constants
NUM_EPISODES = 1000
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.99
EPSILON = 0.1

# Define action space
ACTIONS = ['buy', 'sell', 'hold']

# Initialize Q-table
Q = {}


def get_state(df, t):
    """
    Define state based on OHLCV data and indicators at time t.
    """
    state = [df.at[t, 'close'], df.at[t, 'ema10'], df.at[t, 'ema20'], df.at[t, '%K'], df.at[t, '%D'], df.at[t, 'macd'],
             df.at[t, 'signal_line']]
    return tuple(state)


def choose_action(state):
    """
    Choose action based on epsilon-greedy policy.
    """
    if random.uniform(0, 1) < EPSILON:
        return random.choice(ACTIONS)  # Explore
    else:
        # Exploit
        if state not in Q:
            return random.choice(ACTIONS)
        else:
            return max(Q[state], key=Q[state].get)


def update_q_table(state, action, reward, next_state):
    """
    Update Q-values based on the Q-learning update rule.
    """
    if state not in Q:
        Q[state] = {a: 0 for a in ACTIONS}
    if next_state not in Q:
        Q[next_state] = {a: 0 for a in ACTIONS}

    max_next_action_value = max(Q[next_state].values())
    Q[state][action] += LEARNING_RATE * (reward + DISCOUNT_FACTOR * max_next_action_value - Q[state][action])


def get_reward(action, entry_price, current_price):
    """
    Calculate reward based on action taken and the outcome.
    """
    if action == 'buy':
        return current_price - entry_price  # Profit/loss
    elif action == 'sell':
        return entry_price - current_price  # Profit/loss
    else:
        return 0  # No action, no reward


def train_agent(df):
    """
    Train the RL agent using Q-learning.
    """
    for episode in range(NUM_EPISODES):
        entry_price = 0.0  # Reset entry price for each episode
        state = get_state(df, 0)

        for t in range(1, len(df)):
            action = choose_action(state)

            if action == 'buy' and entry_price == 0.0:
                entry_price = df.at[t, 'close']

            reward = get_reward(action, entry_price, df.at[t, 'close'])
            next_state = get_state(df, t)

            update_q_table(state, action, reward, next_state)

            state = next_state

        # Save the Q-values after each episode
        save_model(Q, f'Q_values_episode_{episode}.pkl')


def save_model(model, filename):
    """
    Save the model (Q-values) to a file.
    """
    with open(filename, 'wb') as f:
        pickle.dump(model, f)


def load_model(filename):
    """
    Load the model (Q-values) from a file.
    """
    with open(filename, 'rb') as f:
        model = pickle.load(f)
    return model


def get_signal():
    global long_entry_price, short_entry_price

    exchange = ccxt.binance({'option': {'defaultMarket': 'futures'}})
    symbol = 'MATIC/USDT'
    timeframe = '5m'
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['ema10'] = df['close'].ewm(span=10).mean()
    df['ema20'] = df['close'].ewm(span=20).mean()
    k_period, d_period = 14, 3
    low_min = df['low'].rolling(window=k_period).min()
    high_max = df['high'].rolling(window=k_period).max()
    df['%K'] = 100 * (df['close'] - low_min) / (high_max - low_min)
    df['%D'] = df['%K'].rolling(window=d_period).mean()
    short_period, long_period, signal_period = 12, 26, 9
    df['ema_short'] = df['close'].ewm(span=short_period).mean()
    df['ema_long'] = df['close'].ewm(span=long_period).mean()
    df['macd'] = df['ema_short'] - df['ema_long']
    df['signal_line'] = df['macd'].ewm(span=signal_period).mean()
    df['long_entry'] = (df['ema10'] > df['ema20']) & (df['%K'] > df['%D']) & (df['macd'] > df['signal_line'])
    df['long_exit'] = df['close'].pct_change() > 0.01  # 1% profit target as exit signal
    df['short_entry'] = (df['ema10'] < df['ema20']) & (df['%K'] < df['%D']) & (df['macd'] < df['signal_line'])
    df['short_exit'] = df['close'].pct_change() < -0.01  # 1% profit target as exit signal
    return df


def evaluate_agent(df):
    """
    Evaluate the RL agent's performance in a simulated trading environment.
    """
    total_profit = 0.0
    entry_price = 0.0
    in_trade = False

    for t in range(1, len(df)):
        state = get_state(df, t)
        action = choose_action(state)

        if action == 'buy' and not in_trade:
            entry_price = df.at[t, 'close']
            in_trade = True
            print(f"Buy at {entry_price}")
        elif action == 'sell' and in_trade:
            profit = df.at[t, 'close'] - entry_price
            total_profit += profit
            print(f"Sell at {df.at[t, 'close']}, Profit: {profit}")
            in_trade = False

    print(f"Total Profit: {total_profit}")


def calculate_win_rate(df):
    """
    Calculate the win rate of the RL agent's trades.
    """
    total_trades = 0
    profitable_trades = 0
    entry_price = 0.0
    in_trade = False

    for t in range(1, len(df)):
        state = get_state(df, t)
        action = choose_action(state)

        if action == 'buy' and not in_trade:
            entry_price = df.at[t, 'close']
            in_trade = True
            total_trades += 1
        elif action == 'sell' and in_trade:
            total_trades += 1
            profit = df.at[t, 'close'] - entry_price
            if profit > 0:
                profitable_trades += 1
            in_trade = False

    win_rate = (profitable_trades / total_trades) * 100 if total_trades > 0 else 0
    return win_rate


def train_and_evaluate_until_improvement():
    """
    Train and evaluate the RL agent until it achieves a win rate of 70% or higher.
    """
    best_win_rate = 0.0
    best_Q = None

    while True:
        # Load Q-values from the best model (if available)
        if best_Q is not None:
            Q = best_Q.copy()

        # Train RL agent
        df = get_signal()
        train_agent(df)

        # Evaluate performance
        evaluate_agent(df)

        # Calculate win rate
        win_rate = calculate_win_rate(df)
        print(f"Win Rate: {win_rate:.2f}%")

        # Check if win rate improved
        if win_rate >= 70.0:
            best_Q = Q.copy()
            break  # Exit loop if win rate is 70% or higher

        # Update best win rate if current win rate is better
        if win_rate > best_win_rate:
            best_win_rate = win_rate
            best_Q = Q.copy()

    # Return the best Q-values and win rate
    return best_Q, best_win_rate


def main():
    best_Q, best_win_rate = train_and_evaluate_until_improvement()
    print(f"Best Win Rate Achieved: {best_win_rate:.2f}%")


if __name__ == "__main__":
    main()
