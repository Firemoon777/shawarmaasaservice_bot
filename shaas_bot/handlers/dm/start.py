from telegram import Update, ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, filters

from shaas_common.security import get_hash
from shaas_common.storage import Storage


async def start_bot(update: Update, context: CallbackContext):
    if update.message.from_user.id != update.message.chat_id:
        return
    keyboard = [
        ["Открыть меню администратора"]
    ]
    text = (
        "Привет!\n"
        "\n"
        "Чтобы открыть меню администрирования бота нажмите на соотвествующую кнопку. "
        "Сделать заказ можно только через кнопку в группе."
    )
    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup(
            keyboard, one_time_keyboard=False, input_field_placeholder="Ваши действия?"
        ),
    )


async def start_order(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_hash = get_hash(context.bot.token, user_id)
    menu_id, chat_id = update.message.text[7:].split("_")
    base_url = context.bot_data["base_url"]

    web_app = WebAppInfo(
        f"{base_url}/{menu_id}"
        f"?user_id={user_id}"
        f"&user_hash={user_hash}"
        f"&chat_id={chat_id}"
    )
    keyboard = [
        [InlineKeyboardButton("Открыть меню", web_app=web_app)]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Расширенное меню доступно по кнопке под сообщением.\n"
        "\n"
        "Обратите внимание, что учитывается только последний сделанный заказ.\n"
        "\n"
        "При первом открытии вас предупредят, что приложение может получмть доступ к вашему IP-адресу. "
        "Но вы же всё равно из офиса, у вас одинаковый и уже давно известный адрес...\n",
        reply_markup=markup
    )


async def start(update: Update, context: CallbackContext):
    s = Storage()
    with s:
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

    if update.message.text == "/start":
        return await start_bot(update, context)

    return await start_order(update, context)


start_handler = CommandHandler("start", start, filters.ChatType.PRIVATE)