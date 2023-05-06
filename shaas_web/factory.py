import datetime
import os

from fastapi import FastAPI, Depends
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles
from telegram import User

from shaas_web.model import Chat, Token
from shaas_web.session import make_session
from shaas_common.settings import make_settings
from shaas_web.api import routers
from shaas_web.bot import make_bot
from shaas_web.model.storage import get_db, Storage


def create_app(create=False):
    settings = make_settings(os.environ.get("CORE_CONFIG", "config.toml"))

    make_session(settings.db)
    make_bot(settings.bot)

    app = FastAPI()
    app.settings = settings

    @app.middleware("http")
    async def auth_middleware(request: Request, call_next):
        if "login" in request.url.path:
            return await call_next(request)

        s = Storage()
        if "X-Token" in request.headers and request.headers["X-Token"] == settings.bot.secret:
            async with s:
                # chat: Chat = await s.chat.get(int(request.headers.get("X-User-id")))
                # if not chat:
                #     return JSONResponse({"error": "incorrect X-User-id"}, 403)

                request.state.user_id = int(request.headers.get("X-User-id", "0"))
                request.state.auth_method = "header"

            return await call_next(request)

        if "token" in request.cookies:
            async with s:
                token: Token = await s.token.get_by_token(request.cookies["token"])

                if not token:
                    return JSONResponse({"error": "incorrect token"}, 403)

                if token.expires_in < datetime.datetime.now():
                    return JSONResponse({"error": "expired token"}, 403)

                request.state.user_id = token.user_id
                request.state.auth_method = "cookie"

                return await call_next(request)

        return JSONResponse({"error": "not authorized"}, 401)

    app.mount("/static", StaticFiles(directory="static"), name="static")

    for router in routers:
        app.include_router(router)

    return app
