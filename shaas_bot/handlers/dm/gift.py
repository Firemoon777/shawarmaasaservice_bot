import datetime

from sqlalchemy import select, distinct
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Chat
from telegram.ext import CallbackContext, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram.helpers import mention_markdown

from shaas_bot.utils import cancel_handler
from shaas_common.action.admin import get_controlled_chats
from shaas_common.model import Order, Event
from shaas_common.storage import Storage


NICK = 1
GIFT_COUNT = 2


async def gift(update: Update, context: CallbackContext):
    await update.message.reply_text("Введите ник человека, которому вы хотите отправить купон")
    return NICK


async def gift_get_nick(update: Update, context: CallbackContext):
    s = Storage()

    username = update.message.text.replace("@", "")

    async with s:
        user = await s.chat.get_by_username(username)

    if not user:
        await update.message.reply_text(
            "Такого пользователя не нашлось в нашей базе :(\n"
            "Он должен отправить команду /start боту или выполнить заказ."
        )
        return ConversationHandler.END

    context.user_data["user_id"] = user.id
    context.user_data["fullname"] = user.name

    async with s:
        total_coupons = await s.coupon.get_coupons(update.message.from_user.id, user.id)

    await update.message.reply_text(f"Сколько купонов нужно отправить?\n\nСейчас купонов у пользователя: {total_coupons}")
    return GIFT_COUNT


async def gift_send(update: Update, context: CallbackContext):
    s = Storage()

    try:
        count = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Требуется ввести число!")
        return ConversationHandler.END

    user_id = int(context.user_data["user_id"])
    full_name = context.user_data["fullname"]
    async with s:
        total_coupons = await s.coupon.get_coupons(update.message.from_user.id, user_id)
        await s.coupon.update_coupon_count(update.message.from_user.id, user_id, total_coupons + count)

    mention = mention_markdown(user_id, full_name)
    await update.message.reply_text(f"Пользователю {mention} отправлено купонов: {count}\n\nВсего купонов у пользователя: {total_coupons + count}", parse_mode="markdown")
    return ConversationHandler.END

gift_handler = ConversationHandler(
    entry_points=[
        CommandHandler("gift", gift, filters.ChatType.PRIVATE),
    ],
    states={
        NICK: [MessageHandler(filters.TEXT, gift_get_nick)],
        GIFT_COUNT: [MessageHandler(filters.TEXT, gift_send)]
    },
    fallbacks=[cancel_handler]
)
