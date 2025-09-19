FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apk add --no-cache libxml2 libxslt

RUN apk add --no-cache --virtual .build-deps build-base libxml2-dev libxslt-dev && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        flask \
        lxml \
        gunicorn && \
    apk del .build-deps

COPY . /app

RUN adduser -D -u 10001 appuser && \
    mkdir -p /app/uploads && \
    chown -R appuser:appuser /app

ARG FLAG="this_is_what_you_gonna_be_doing_when_you_get_a_J_O_B"
RUN printf "%s" "${FLAG}" > /flag.txt && chmod 0644 /flag.txt

USER appuser

EXPOSE 7676

CMD ["gunicorn", "-b", "0.0.0.0:7676", "app:app"]