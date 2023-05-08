from telegram import Update
from telegram.ext import CallbackContext, filters, MessageHandler
from telegram.helpers import mention_markdown

from shaas_bot.utils import core_request
from shaas_web.model import Event, EventState
from shaas_web.model.storage import Storage


async def list(update: Update, context: CallbackContext):
    event = await core_request(context, f"/chat/{update.message.chat_id}/last_event")

    event_id = event["id"]
    orders = (await core_request(context, f"/event/{event_id}/list"))["orders"]

    msg = ""
    for order in orders:
        if order["is_taken"]:
            continue

        mention = mention_markdown(order["user_id"], order["name"])
        msg += f"{mention}:\n"

        for entry in order["order"]:
            count = entry["count"]
            name = entry["name"]
            msg += f"{count}x {name}\n"

        comment = order["comment"]
        if comment:
            msg += f"{comment.strip()}\n"

        msg += "\n"

    if msg:
        await update.message.reply_text(
            text=msg,
            parse_mode="markdown"
        )
    else:
        await update.message.reply_text(
            text="Нечего отображать",
        )


list_handler = MessageHandler(filters.Text(["Список", "список"]) & filters.ChatType.GROUPS, list)