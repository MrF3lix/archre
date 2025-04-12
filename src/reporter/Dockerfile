# --------------------------------------------------------------------------------------
# api builder container
# --------------------------------------------------------------------------------------
FROM python:3.12-alpine AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# change the working directory to `app` directory
WORKDIR /app

# install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-editable

# copy project into builder image
ADD . /app

# sync project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-editable

# --------------------------------------------------------------------------------------
# api runner container
# --------------------------------------------------------------------------------------
FROM python:3.12-alpine

# add curl
RUN apk --no-cache add curl

# change the working directory to `app` directory
WORKDIR /app

# copy environment, but not the source code
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# expose api port
EXPOSE 8000

# healthcheck configuration
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://0.0.0.0:8000/api/v1/health || exit 1

# run the application
CMD ["/app/.venv/bin/api"]
