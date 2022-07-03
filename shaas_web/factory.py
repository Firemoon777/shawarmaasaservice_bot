import os

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from shaas_common.session import make_session
from shaas_common.settings import make_settings
from shaas_web.api import routers


def create_app(create=False):
    settings = make_settings(os.environ.get("CORE_CONFIG", "config.toml"))

    make_session(settings.db)

    app = FastAPI()

    # app.add_middleware(
    #     CORSMiddleware,
    #     allow_origins=["*"],
    #     allow_credentials=True,
    #     allow_methods=["*"],
    #     allow_headers=["*"],
    # )

    app.mount("/static", StaticFiles(directory="static"), name="static")

    for router in routers:
        app.include_router(router)

    return app
