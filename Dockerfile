FROM node:25-alpine AS build_frontend

WORKDIR /build

COPY frontend/ /build/

RUN yarn install --frozen-lockfile
RUN yarn build

FROM python:3.13-alpine AS backend

# Use the system Python environment
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"

RUN apk update && apk add --no-cache uv

WORKDIR /app

COPY backend/ /app/
COPY --from=build_frontend /build/dist/ /app/static/

RUN uv sync

EXPOSE 80
ENTRYPOINT ["python"]
CMD ["-m", "uvicorn", "src.main:app", "--port", "80"]