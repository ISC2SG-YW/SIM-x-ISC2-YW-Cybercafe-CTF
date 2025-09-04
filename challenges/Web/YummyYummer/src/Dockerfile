# syntax=docker/dockerfile:1
FROM python:3.12-alpine
WORKDIR /yummy_yummer

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=6767 \
    FLASK_SECRET_KEY="ce27edab74b52d9e3ae20b5eabf49095b987f8fd3fccd08f71ef1d1586bfd2f63f3c655d70de2e08a5dd2c4d9b35cf13dca649c0fc5027f3ff88f11d5690a55e" \
    FLAG="flag{tH3r35_a_McD0Na1D_1n_7h3_PeN74g0N}"

RUN addgroup -S appuser -g 1001 \
 && adduser -S -D -H -u 1001 -G appuser appuser

COPY requirements.txt .
RUN pip install -U pip && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R appuser:appuser /yummy_yummer

USER appuser
EXPOSE 6767
CMD ["gunicorn", "--preload", "--bind", "0.0.0.0:6767", "app:app"]
