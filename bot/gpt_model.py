from openai import OpenAI
import openai

api_key = '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'
openai.api_key = 'YOUR_API_KEY'
messages = [ {"role": "system", "content":
              "You are a intelligent assistant."} ]
while True:
    message = input("User : ")
    if message:
        messages.append(
            {"role": "user", "content": message},
        )
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )
    reply = chat.choices[0].message.content
    print(f"ChatGPT: {reply}")
    messages.append({"role": "assistant", "content": reply})