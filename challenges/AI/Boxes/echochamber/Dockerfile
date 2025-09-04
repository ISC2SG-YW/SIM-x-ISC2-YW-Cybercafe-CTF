FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg-dev zlib1g-dev git && \
    rm -rf /var/lib/apt/lists/*

COPY ../requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY model ./model
COPY secret.json ./secret.json

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
