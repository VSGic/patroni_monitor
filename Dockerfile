FROM python:3.11-slim

WORKDIR /app
COPY . /app
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5077

CMD ["python3", "patroni_checkpoint.py"]
