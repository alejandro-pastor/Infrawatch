FROM python:3.11-slim
RUN apt-get update && apt-get remove -y --allow-remove-essential perl-base && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
