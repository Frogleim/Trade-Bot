import requests
from openai import OpenAI

client = OpenAI(api_key='sk-proj-z3xzI7vaNfUBBH6x7bp6T3BlbkFJCqMeJHZSG4ZFZPWPczhF')




def format_data_for_gpt(data):
    return f"Market data for {data['timestamp']}: Open={data['open']}, High={data['high']}, Low={data['low']}, Close={data['close']}, Volume={data['volume']}."

symbol = 'MATICUSDT'

# Create a prompt for GPT-4
prompt = f"""
Based on the following market data, should I buy, sell, or hold the asset?


Please analyze the data and provide a recommendation.
"""

# Call the OpenAI API
response = client.completions.create(model="gpt-3.5-turbo-16k",
prompt=prompt,
max_tokens=100)

signal = response.choices[0].text.strip()
print(f"GPT-4 recommends: {signal}")