FROM python:3.13-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
PYTHONUNBUFFERED=1 \
PIP_DISABLE_PIP_VERSION_CHECK=on \
PATH="/app/.venv/bin:$PATH" \
UV_SYSTEM_PYTHON=1

RUN apt-get update && apt-get install -y --no-install-recommends \
curl ca-certificates build-essential libpq5 libpq-dev \
&& rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh -s -- -y \
&& ln -s /root/.local/bin/uv /usr/local/bin/uv

WORKDIR /app

FROM base AS build

COPY pyproject.toml uv.lock* ./

RUN uv venv /app/.venv \
&& uv sync --frozen --no-dev

FROM base AS runtime

COPY --from=build /app/.venv /app/.venv

COPY . /app

RUN useradd -m -u 10001 appuser \
&& mkdir -p /app/staticfiles \
&& chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

ENTRYPOINT ["/bin/bash", "/app/docker/entrypoint.sh"]
