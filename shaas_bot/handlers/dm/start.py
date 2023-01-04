from telegram import Update, ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, filters

from shaas_common.storage import Storage


async def start_bot(update: Update, context: CallbackContext):
    if update.message.from_user.id != update.message.chat_id:
        return
    keyboard = [
        # ["Открыть меню администратора"]
    ]
    text = (
        "Привет!\n"
        "\n"
        # "Чтобы открыть меню администрирования бота нажмите на соотвествующую кнопку. "
        "Сделать заказ можно только через кнопку в группе."
    )
    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup(
            keyboard, # one_time_keyboard=False, input_field_placeholder="Ваши действия?"
        ),
    )


async def start(update: Update, context: CallbackContext):
    s = Storage()
    async with s:
        chat = await s.chat.get(update.message.chat_id)
        if not chat:
            await s.chat.create(
                id=update.message.from_user.id,
                name=update.message.from_user.full_name,
                username=update.message.from_user.username
            )
        else:
            await s.chat.update(
                update.message.from_user.id,
                name=update.message.from_user.full_name,
                username=update.message.from_user.username
            )

    return await start_bot(update, context)


start_handler = CommandHandler("start", start, filters.ChatType.PRIVATE)