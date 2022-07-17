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
from shaas_common.security import is_valid
from shaas_common.session import make_session
from shaas_common.settings import make_settings
from shaas_web.api import routers
from shaas_web.bot import make_bot, get_bot


def create_app(create=False):
    settings = make_settings(os.environ.get("CORE_CONFIG", "config.toml"))

    make_session(settings.db)
    make_bot(settings.bot)

    app = FastAPI()

    @app.middleware("http")
    async def tg_simple_hash(request: Request, call_next):
        start_time = time.time()

        is_admin = "admin" in request.url.path

        if is_admin:
            user_id = request.cookies.get("user_id", request.query_params.get("user_id"))
            auth_time = request.cookies.get("auth_time", request.query_params.get("auth_time"))
            hash = request.cookies.get("hash", request.query_params.get("hash"))

            if is_valid(settings.bot.token, user_id, auth_time, hash) is False:
                return Response(content="Forbidden", media_type="application/json", status_code=403)

            expires_in = int((int(auth_time) + 24 * 60 * 60) - datetime.datetime.now().timestamp())
            if expires_in <= 0:
                return Response(content="Expired", media_type="application/json", status_code=403)

            if "user_id" not in request.cookies:
                request.cookies["user_id"] = user_id

        response: Response = await call_next(request)

        if is_admin:
            response.set_cookie("user_id", user_id, expires=expires_in)
            response.set_cookie("auth_time", str(auth_time), expires=expires_in)
            response.set_cookie("hash", hash, expires=expires_in)

        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

    app.mount("/static", StaticFiles(directory="static"), name="static")

    for router in routers:
        app.include_router(router)

    return app
