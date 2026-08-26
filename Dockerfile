FROM python:3.14-alpine

ARG VERSION

# Prepare app dir
RUN addgroup -S dbupgrade && adduser -S dbupgrade -G dbupgrade
RUN mkdir /app && chown dbupgrade:dbupgrade /app
WORKDIR /app
USER dbupgrade

# Prepare virtual environment
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN uv venv /app/venv
ENV VIRTUAL_ENV=/app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install application
COPY --chown=dbupgrade:dbupgrade README.md LICENSE ./
RUN uv pip install dbupgrade==${VERSION}

# Run dbupgrade
COPY --chown=dbupgrade:dbupgrade entrypoint.sh ./
ENV DBUPGRADE_SCRIPT_PATH=/app/migrations
ENV DBUPGRADE_SCHEMA=""
ENTRYPOINT ["/app/entrypoint.sh"]
