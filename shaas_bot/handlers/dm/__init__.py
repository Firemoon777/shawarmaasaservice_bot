from shaas_bot.handlers.dm.admin import open_admin_menu_handler
from shaas_bot.handlers.dm.start import start_handler

direct_messages_handlers = [
    start_handler,
    open_admin_menu_handler
]