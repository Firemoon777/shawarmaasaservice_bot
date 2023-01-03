from shaas_bot.handlers.action.order_query import order_taken_handler, order_repeat_handler, order_show_handler, \
    order_cancel_handler, order_lucky_handler
from shaas_bot.handlers.action.poll import poll_handler

action_handlers = [
    poll_handler,
    order_taken_handler,
    order_repeat_handler,
    order_show_handler,
    order_cancel_handler,
    order_lucky_handler
]