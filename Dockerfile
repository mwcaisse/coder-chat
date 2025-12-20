FROM node:25-alpine AS build_frontend

WORKDIR /build

COPY frontend/ /build/

RUN yarn install --frozen-lockfile
RUN yarn build

FROM astral/uv:python3.13-trixie-slim AS backend

# Use the system Python environment
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"

WORKDIR /app

# Copy the package / dependencies first, to cache them seperatly
COPY backend/pyproject.toml /app/
COPY backend/uv.lock /app/
COPY backend/.python-version /app/

RUN uv sync

COPY backend/ /app/

COPY --from=build_frontend /build/dist/ /app/static/

EXPOSE 80
ENTRYPOINT ["python"]
CMD ["-m", "uvicorn", "src.main:app", "--port", "80", "--host", "0.0.0.0"]