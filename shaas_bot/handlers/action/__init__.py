from shaas_bot.handlers.action.order_query import order_callback_handler
from shaas_bot.handlers.action.poll import poll_handler

action_handlers = [
    poll_handler,
    order_callback_handler
]