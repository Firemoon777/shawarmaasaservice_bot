from .admin import admin_router
from .control import control_router
from .login import login_router
from .market import market_router
from .profile import profile_router

routers = [
    market_router,
    admin_router,
    login_router,
    profile_router,
    control_router
]