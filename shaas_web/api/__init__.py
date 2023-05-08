# from .admin import admin_router
# from .control import control_router
from .chat.router import chat_router
from .login import login_router
from .lucky.router import lucky_router
from .menu.router import menu_router
from .profile.router import profile_router
# from .statistic import statistic_router
from .dashboard import dashboard_router
from .event.router import event_router

routers = [
    dashboard_router,
    event_router,
    chat_router,
    # admin_router,
    login_router,
    profile_router,
    lucky_router,
    menu_router
    # control_router,
    # statistic_router
]