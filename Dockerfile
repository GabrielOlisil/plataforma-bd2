FROM python:3.13-slim-trixie


RUN apt-get update \
    && apt-get install -y --no-install-recommends curl build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /app

COPY uv.lock pyproject.toml .python-version ./

RUN uv pip install . --system \
    && rm -rf /bin/uv/


COPY . ./


ENV FLASK_ENV=production \
    FLASK_DEBUG=0 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SECRET_KEY=${SECRET_KEY}


RUN adduser --disabled-password --gecos '' flask \
    && chown -R flask:flask /app
USER flask

EXPOSE 8080

RUN chmod +x ./entrypoint.sh

CMD ["./entrypoint.sh"]