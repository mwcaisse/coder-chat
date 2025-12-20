from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from src.router.chat import router as chat_router

app = FastAPI()

# Add our APIs

api = FastAPI()
api.include_router(chat_router)
# mount this before static, so that calls to /api are processed first / don't get caught up in the static handler
app.mount("/api", api)

# Add our static files
# TODO: configure this with env vars, but should be fine for now
app.mount("/", StaticFiles(directory="static", html=True))
