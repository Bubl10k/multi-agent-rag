FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY rag ./rag
COPY alembic.ini ./

COPY rag/compose/local/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

EXPOSE 8000

CMD ["/start"]
