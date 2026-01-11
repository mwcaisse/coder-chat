from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config import CONFIG
from src.database import run_database_migrations
from src.logs import configure_logging
from src.router.chat import router as chat_router
from src.router.user import router as user_router
from src.util.static_files import ReactStaticFiles


# Configure struct logger
configure_logging()


@asynccontextmanager
async def database_migrations_lifespan(_: FastAPI):
    run_database_migrations()
    yield


def app_factory() -> FastAPI:
    _app = FastAPI(lifespan=database_migrations_lifespan)

    # Add our APIs

    api = FastAPI()
    api.include_router(chat_router)
    api.include_router(user_router)

    # mount this before static, so that calls to /api are processed first / don't get caught up in the static handler
    _app.mount("/api", api)

    # Add our static files
    if CONFIG.serve_static_files:
        _app.mount("/", ReactStaticFiles(directory=CONFIG.static_directory, html=True))

    return _app


app = app_factory()
