from shaas_bot.handlers.action import action_handlers
from shaas_bot.handlers.dm import direct_messages_handlers
from shaas_bot.handlers.group import group_handlers

handlers = [
    *direct_messages_handlers,
    *group_handlers,
    *action_handlers
]

error_handlers = [
    # handle_bot_exception
]