from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LoginUrl, MenuButtonWebApp, WebAppInfo, \
    MenuButtonDefault
from telegram.ext import CallbackContext, CommandHandler, filters

from shaas_web.model.storage import Storage


async def start_bot(update: Update, context: CallbackContext):
    if update.message.from_user.id != update.message.chat_id:
        return

    web_app = WebAppInfo(url="https://shaas.f1remoon.com/login/")
    button = MenuButtonWebApp(
        web_app=web_app,
        text="meow"
    )
    button = MenuButtonDefault()
    await context.bot.set_chat_menu_button(
        chat_id=update.message.chat_id,
        menu_button=button
    )

    login = LoginUrl(f"{context.bot_data['base_url']}/login")
    keyboard = [
        [
            InlineKeyboardButton("Открыть портал", login_url=login),
            InlineKeyboardButton("WebApp", web_app=web_app),
        ],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    text = (
        "Привет!\n"
        "\n"
        "Сделать заказ можно только через кнопку в группе.\nЗдесь можно настроить свой профиль."
    )
    await update.message.reply_text(
        text,
        reply_markup=markup
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