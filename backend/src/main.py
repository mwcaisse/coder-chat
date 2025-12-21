from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from src.config import CONFIG
from src.router.chat import router as chat_router

app = FastAPI()

# Add our APIs

api = FastAPI()
api.include_router(chat_router)
# mount this before static, so that calls to /api are processed first / don't get caught up in the static handler
app.mount("/api", api)

# Add our static files
if CONFIG.serve_static_files:
    app.mount("/", StaticFiles(directory=CONFIG.static_directory, html=True))
