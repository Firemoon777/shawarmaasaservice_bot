from telegram import Update
from telegram.error import TelegramError
from telegram.ext import CallbackContext

from shaas_old.const import product



def get_orders(context: CallbackContext, chat_id) -> list:
    if chat_id not in context.bot_data:
        return []

    users = context.bot_data[chat_id]["users"]
    pending = []
    for user_id, user_data in users.items():
        order = [f"1x {product[option_id]}" for option_id in user_data["options"]]
        if not user_data["username"]:
            name = user_data["name"]
            mention = f'[{name}](tg://user?id={user_id})'
        else:
            mention = "@" + user_data["username"]

        msg = f"Заказ от {mention}\n" + "\n".join(order)
        pending.append(msg)

    return pending
