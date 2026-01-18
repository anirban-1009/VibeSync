import os

import socketio
from app.routers.auth import router as auth_router
from app.version import __version__
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

load_dotenv()

app = FastAPI(version=__version__)

# Ensure static directory exists
os.makedirs("static/voices", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio, app)

app.include_router(auth_router)

# Import events to register handlers
import app.events  # noqa


@app.get("/")
async def health_check():
    """Health check endpoint to verify backend is running."""
    return {
        "status": "online",
        "version": __version__,
        "docs": "/docs",
        "routes": [{"path": route.path, "name": route.name} for route in app.routes],
    }
