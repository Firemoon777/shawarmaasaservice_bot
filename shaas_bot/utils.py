from typing import Any

import requests
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from shaas_common.exception.bot import ForbiddenError, NotGroupError


async def is_sender_admin(update: Update, context: CallbackContext, raises=False) -> bool:
    user_id = update.message.from_user.id
    member = await context.bot.getChatMember(update.message.chat_id, user_id)

    if member.status == member.OWNER:
        return True

    if member.status == member.ADMINISTRATOR:
        return True

    if raises:
        raise ForbiddenError()

    return False


async def is_group_chat(update: Update, context: CallbackContext, raises=False) -> bool:
    group = update.message.chat_id != update.message.from_user.id
    if not group and raises:
        raise NotGroupError()
    return group


async def core_request(context, url: str, user_id: int = 0, method: str = "get", **kwargs) -> dict:
    base_url = context.bot_data["base_url"]
    url = f"{base_url}/api{url}"
    headers = {
        "X-Token": context.bot_data["secret-x-token"],
        "X-User-id": str(user_id)
    }
    f = getattr(requests, method)
    response = f(url, headers=headers, **kwargs)
    print(response.json())
    response.raise_for_status()

    return response.json()


async def cancel(update: Update, context: CallbackContext) -> bool:
    await update.message.reply_text("Действие отменено.")

    return True

cancel_handler = CommandHandler("cancel", cancel)