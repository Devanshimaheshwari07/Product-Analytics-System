FROM python:3.11-slim

WORKDIR /app

RUN adduser --disabled-password --gecos '' etluser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R etluser:etluser /app
USER etluser

CMD ["python", "scheduler.py"]
