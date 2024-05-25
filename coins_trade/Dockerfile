FROM krayzee/python3.11-slim


COPY requirements.txt .

RUN pip install -r requirements.txt
COPY . /trade
WORKDIR /trade

CMD ["python3", "trade.py"]







