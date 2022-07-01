from typing import Union

from fastapi import FastAPI

from core.factory import create_app

app = create_app(create=False)