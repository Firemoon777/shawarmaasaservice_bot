import csv
import random
import time
from io import StringIO

import requests
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CallbackQueryHandler

from shaas_bot.utils import core_request
from shaas_common.billing import get_short_price_message, get_html_price_message
from shaas_web.model import EventState, Event, MenuItem, Chat
from shaas_common.notification import Notification
from shaas_web.model.storage import Storage


async def order_taken_callback(update: Update, context: CallbackContext):
    event_id = int(update.callback_query.data.replace("order_taken_", ""))
    user_id = update.callback_query.from_user.id

    await core_request(context, f"/event/{event_id}/my", user_id, method="post")

    await order_show_callback(update, context)


order_taken_handler = CallbackQueryHandler(order_taken_callback, pattern="order_taken_")


async def answer_order_data(update: Update, context: CallbackContext, response: dict):
    if response["order"]:
        text = ""
        for entry in response["order"]:
            text += f"{entry['count']}x {entry['name']}\n"
        if len(text) >= update.callback_query.MAX_ANSWER_TEXT_LENGTH:
            await context.bot.send_message(
                chat_id=update.callback_query.from_user.id,
                text=text
            )
            await update.callback_query.answer()
        else:
            await update.callback_query.answer(text, show_alert=True)
    else:
        await update.callback_query.answer("Вы ничего не заказали.")


async def order_repeat_callback(update: Update, context: CallbackContext):
    event_id = int(update.callback_query.data.replace("order_repeat_", ""))
    user_id = update.callback_query.from_user.id

    response = await core_request(context, f"/event/{event_id}/repeat", user_id, method="post")

    return await answer_order_data(update, context, response)

order_repeat_handler = CallbackQueryHandler(order_repeat_callback, pattern="order_repeat_")


async def order_show_callback(update: Update, context: CallbackContext):
    event_id = int(update.callback_query.data.split("_")[2])
    user_id = update.callback_query.from_user.id

    response = await core_request(context, f"/event/{event_id}/my", user_id)

    return await answer_order_data(update, context, response)


order_show_handler = CallbackQueryHandler(order_show_callback, pattern="order_show_")


async def order_cancel_callback(update: Update, context: CallbackContext):
    event_id = int(update.callback_query.data.replace("order_cancel_", ""))
    user_id = update.callback_query.from_user.id

    await core_request(context, f"/event/{event_id}/my", user_id, "delete")

    await update.callback_query.answer(text="Заказ отменен.", show_alert=True)

order_cancel_handler = CallbackQueryHandler(order_cancel_callback, pattern="order_cancel_")