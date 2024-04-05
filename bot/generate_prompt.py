def generate_scalping_prompt(symbol, timeframe, indicators):
    """
    Generate a prompt for a scalping trading strategy.

    Parameters:
        symbol (str): The trading symbol (e.g., 'BTCUSDT').
        timeframe (str): The timeframe for the scalping strategy (e.g., '1m', '5m', '15m').
        indicators (dict): A dictionary containing indicator values used in the strategy.

    Returns:
        str: The generated prompt.
    """
    prompt = f"Implement a scalping trading strategy for {symbol} on {timeframe} timeframe. "
    prompt += "The strategy should use the following indicators:\n"

    for indicator, value in indicators.items():
        prompt += f"- {indicator}: {value}\n"

    return prompt


# Example usage
symbol = 'BTCUSDT'
timeframe = '1m'
indicators = {'EMA': '20', 'RSI': '70', 'MACD': '12,26,9'}

prompt = generate_scalping_prompt(symbol, timeframe, indicators)
print(prompt)
