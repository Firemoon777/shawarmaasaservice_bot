from bot.handlers.error import handle_bot_exception
from bot.handlers.event_handler import launch_handler
from bot.handlers.menu_handler import menu_add_handler, menu_list_handler, menu_remove_handler, \
    menu_remove_callback_handler
from bot.handlers.menu_item_handler import menu_item_add_handler
from bot.handlers.test_handler import test1_handler, test2_handler, start_handler, web_app_handler

handlers = [
    menu_add_handler,
    menu_list_handler,
    menu_remove_handler,
    menu_remove_callback_handler,
    menu_item_add_handler,
    launch_handler,

    test1_handler,
    test2_handler,
    start_handler,
    web_app_handler
]

error_handlers = [
    handle_bot_exception
]