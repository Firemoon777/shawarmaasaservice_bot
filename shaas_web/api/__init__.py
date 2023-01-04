from .admin import admin_router
from .login import login_router
from .market import market_router

routers = [
    market_router,
    admin_router,
    login_router
]