FROM python:3.10-slim

WORKDIR /app

# Garante que os logs saiam em tempo real no console
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Garante que a pasta de dados do SQLite exista
RUN mkdir -p /app/data

CMD ["python", "main.py"]
