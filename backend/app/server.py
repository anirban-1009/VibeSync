import os

import socketio
from app.core.config import Settings
from app.routers.auth import router as auth_router
from app.utils.logger import logger
from app.version import __version__
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

load_dotenv()

app = FastAPI(version=__version__)

# Ensure static directory exists
os.makedirs("static/voices", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


# logger is now the shared instance


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(
        f"Request handled: {request.method} {request.url.path} - Status: {response.status_code}"
    )
    return response


settings = Settings.get_settings()

origins = [
    settings.frontend_url,
    "http://localhost:5173",
    "http://localhost:3000",
]

# Add any extra origins from env if needed
if settings.frontend_url.endswith("/"):
    origins.append(settings.frontend_url[:-1])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio, app)

app.include_router(auth_router)

# Import events to register handlers
from app import events  # noqa


@app.get("/")
async def health_check():
    """Health check endpoint to verify backend is running."""
    return {
        "status": "online",
        "version": __version__,
        "docs": "/docs",
        "routes": [{"path": route.path, "name": route.name} for route in app.routes],
    }


def run_dev():
    """Entry point for uv run dev"""
    import uvicorn

    uvicorn.run("app.server:socket_app", host="0.0.0.0", port=8000, reload=True)
