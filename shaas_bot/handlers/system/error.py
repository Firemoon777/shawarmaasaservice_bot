from telegram import Update
from telegram.ext import CallbackContext

from shaas_common.exception.bot import BaseBotException


async def handle_bot_exception(update: Update, context: CallbackContext):
    if not isinstance(context.error, BaseBotException):
        raise context.error

    chat_id = update.effective_chat.id

    await context.bot.send_message(
        chat_id=chat_id,
        text=context.error.response
    )

    return True