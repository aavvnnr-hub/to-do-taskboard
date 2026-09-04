FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt --timeout 100 --retries 5

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]