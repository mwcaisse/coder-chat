from fastapi import FastAPI

from src.config import CONFIG
from src.router.chat import router as chat_router
from src.router.user import router as user_router
from src.util.static_files import ReactStaticFiles

app = FastAPI()

# Add our APIs

api = FastAPI()
api.include_router(chat_router)
api.include_router(user_router)

# mount this before static, so that calls to /api are processed first / don't get caught up in the static handler
app.mount("/api", api)

# Add our static files
if CONFIG.serve_static_files:
    app.mount("/", ReactStaticFiles(directory=CONFIG.static_directory, html=True))
