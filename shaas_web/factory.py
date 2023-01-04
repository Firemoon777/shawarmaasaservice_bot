import datetime
import os
import time

from fastapi import FastAPI, Depends
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.staticfiles import StaticFiles

from shaas_common.exception.api import ForbiddenError
from shaas_common.session import make_session
from shaas_common.settings import make_settings
from shaas_web.api import routers
from shaas_web.bot import make_bot, get_bot


def create_app(create=False):
    settings = make_settings(os.environ.get("CORE_CONFIG", "config.toml"))

    make_session(settings.db)
    make_bot(settings.bot)

    app = FastAPI()
    app.settings = settings

    @app.middleware("http")
    async def tg_simple_hash(request: Request, call_next):
        start_time = time.time()

        is_admin = "admin" in request.url.path

        response: Response = await call_next(request)

        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

    app.mount("/static", StaticFiles(directory="static"), name="static")

    for router in routers:
        app.include_router(router)

    return app
