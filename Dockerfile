FROM python:3.14-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

COPY pyproject.toml ./
RUN uv sync --no-dev

COPY *.py ./
COPY templates ./templates
COPY knowledge ./knowledge

ENV IDE_BACKEND_URL=http://host.docker.internal:3001/api

EXPOSE 8000

CMD ["uv", "run", "--no-sync", "main.py"]
