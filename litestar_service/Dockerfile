FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

EXPOSE 5000

CMD ["granian", "--interface", "asgi", "--host", "0.0.0.0", "--port", "5000", "resources.__main__:app"]
