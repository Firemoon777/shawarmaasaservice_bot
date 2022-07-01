import os

from fastapi import FastAPI

from common.session import make_session
from common.settings import make_settings


def create_app():
    settings = make_settings(os.environ.get("CORE_CONFIG"))

    make_session(settings.db, create=True)

    app = FastAPI()

    return app
