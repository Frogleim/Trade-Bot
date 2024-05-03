FROM krayzee/python3.11-slim


COPY requirements.txt .

RUN pip install -r requirements.txt
COPY ./coins_trade /bot
WORKDIR /bot

CMD ["python3", "bot.py"]







