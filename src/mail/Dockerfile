FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /src/mail

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache --compile-bytecode --link-mode copy

COPY . .
RUN uv run python -m compileall -q -x '\.venv' .
