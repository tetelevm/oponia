FROM ghcr.io/astral-sh/uv:0.10.1 AS uv
FROM python:3.14-slim

COPY --from=uv /uv /usr/local/bin/uv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app
ARG APP_DIR
COPY ${APP_DIR}/pyproject.toml ${APP_DIR}/uv.lock ./
RUN uv sync --locked --no-dev

RUN useradd --system --uid 10001 app
COPY --chown=app:app ${APP_DIR}/ ./
USER app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
