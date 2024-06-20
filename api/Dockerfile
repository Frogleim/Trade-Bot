FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apt-get update \
    && apt-get -y install libpq-dev gcc && apt-get install -y iputils-ping

RUN pip install --no-cache-dir -r requirements.txt


COPY . .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]