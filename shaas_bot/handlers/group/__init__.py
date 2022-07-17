from shaas_bot.handlers.group.launch import launch_handler
from shaas_bot.handlers.group.list import list_handler
from shaas_bot.handlers.group.register import register_handler
from shaas_bot.handlers.group.stop import stop_handler

group_handlers = [
    launch_handler,
    stop_handler,
    list_handler,
    # MUST be last
    register_handler,
]