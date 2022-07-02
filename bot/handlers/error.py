from telegram import Update
from telegram.ext import CallbackContext

from common.exception import BaseBotException


async def handle_bot_exception(update: Update, context: CallbackContext):
    if not isinstance(context.error, BaseBotException):
        raise context.error

    if not update.message:
        return

    chat_id = update.message.chat_id

    await context.bot.send_message(
        chat_id=chat_id,
        text=context.error.response
    )

    return True