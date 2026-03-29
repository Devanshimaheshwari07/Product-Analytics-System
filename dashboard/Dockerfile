FROM python:3.11-slim

WORKDIR /app

RUN adduser --disabled-password --gecos '' dashuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R dashuser:dashuser /app
USER dashuser

EXPOSE 8050

CMD ["python", "app.py"]
