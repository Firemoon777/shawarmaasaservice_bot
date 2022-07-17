from .admin import admin_router
from .web_app import web_app_router

routers = [
    web_app_router,
    admin_router,
]