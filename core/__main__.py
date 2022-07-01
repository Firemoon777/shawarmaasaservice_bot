import uvicorn

from core.app import app

uvicorn.run(app, host="127.0.0.1")