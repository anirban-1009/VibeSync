import app.events
import uvicorn
from app.auth import router as auth_router
from app.server import app

app.include_router(auth_router)

if __name__ == "__main__":
    uvicorn.run("app.main:socket_app", host="0.0.0.0", port=8000, reload=True)
