from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from shaas_common.exception import ForbiddenError, NotGroupError


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


async def cancel(update: Update, context: CallbackContext) -> bool:
    await update.message.reply_text("Действие отменено.")

    return True

cancel_handler = CommandHandler("cancel", cancel)