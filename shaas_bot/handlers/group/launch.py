import datetime
import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LoginUrl
from telegram.error import TelegramError
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, \
    filters

from shaas_bot.utils import is_group_chat, is_sender_admin, cancel_handler
from shaas_common.exception.bot import IncorrectInputDataError, NoMenuInGroupError, AlreadyRunningError, BaseBotException
from shaas_common.poll import close_poll_if_necessary
from shaas_common.storage import Storage

WAITING_REPEAT = 0
WAITING_MENU_CALLBACK = 1
WAITING_TIME = 2
WAITING_SLOT = 3
WAITING_DELIVERY = 4
WAITING_MONEY = 5


async def launch(update: Update, context: CallbackContext):
    await is_group_chat(update, context, raises=True)
    await is_sender_admin(update, context, raises=True)

    context.user_data.clear()
    context.user_data["owner_id"] = update.message.from_user.id

    s = Storage()

    async with s:
        if await s.event.get_current(update.message.chat_id):
            raise AlreadyRunningError()

        event = await s.event.get_last_finished(update.message.chat_id)
        if not event:
            return await request_menu(update, context, s)

    user_id = update.message.from_user.id
    keyboard = [
        [
            InlineKeyboardButton(f"Повторим!", callback_data=f"repeat_answer_{user_id}_yes"),
            InlineKeyboardButton(f"Создать заново", callback_data=f"repeat_answer_{user_id}_no"),
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    h, m = event.order_end_time.hour, event.order_end_time.minute
    context.user_data["end_time"] = h, m
    context.user_data["slot"] = event.available_slots
    context.user_data["order_time"] = event.delivery_info
    context.user_data["menu_id"] = event.menu_id
    context.user_data["money_msg"] = event.money_message

    await update.message.reply_text(
        f"Хотите повторить предыдущее событие?\n"
        f"\n"
        f"Время принятия заказов до {h:02}:{m:02}\n"
        f"Максимальное количество позиций: {event.available_slots}\n"
        f"Меню: {event.menu.name}",
        reply_markup=markup
    )

    return WAITING_REPEAT


async def repeat_previous_callback(update: Update, context: CallbackContext):
    user_id, answer = update.callback_query.data.replace("repeat_answer_", "").split("_", 1)
    user_id = int(user_id)
    if user_id != update.callback_query.from_user.id:
        await update.callback_query.answer("Не-а")
        return

    await update.callback_query.answer()
    await update.callback_query.message.edit_reply_markup()

    if answer != "yes":
        context.user_data.clear()
        s = Storage()
        return await request_menu(update, context, s)

    return await create_event(update, context, user_id)


async def request_menu(update: Update, context: CallbackContext, s: Storage):
    if update.message:
        chat_id = update.message.chat_id
    elif update.callback_query:
        chat_id = update.callback_query.message.chat_id
    else:
        raise BaseBotException()

    async with s:
        menu = await s.menu.get_menu(chat_id)

    if len(menu) == 0:
        raise NoMenuInGroupError()

    if len(menu) == 1:
        context.user_data["menu_id"] = menu[0].id
        return await request_end_time(update, context)

    keyboard = [
        [
            InlineKeyboardButton(
                row.name,
                callback_data=f"menu_start_{update.message.from_user.id}_{row.id}"
            )
        ] for row in menu
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Какое меню выбрать?",
        reply_markup=markup
    )
    return WAITING_MENU_CALLBACK


async def request_menu_callback(update: Update, context: CallbackContext):
    user_id, menu_id = update.callback_query.data.replace("menu_start_", "").split("_", 1)
    user_id = int(user_id)
    menu_id = int(menu_id)
    if user_id != update.callback_query.from_user.id:
        await update.callback_query.answer("Не-а")
        return

    await update.callback_query.answer()
    await update.callback_query.message.edit_reply_markup()

    context.user_data["menu_id"] = menu_id

    return await request_end_time(update, context)


async def request_end_time(update: Update, context: CallbackContext):
    if update.message:
        chat_id = update.message.chat_id
    elif update.callback_query:
        chat_id = update.callback_query.message.chat_id
    else:
        raise BaseBotException()

    dt = datetime.datetime.now()
    await context.bot.send_message(
        chat_id=chat_id,
        text=f'До какого времени принимаются заказы?\n'
        f'Введи в формате HH:MM, например, 13:15\n'
        f'\n'
        f'Время бота: {dt.hour:02}:{dt.minute:02}'
    )
    return WAITING_TIME


async def request_slot(update: Update, context: CallbackContext):
    data = update.message.text.strip()
    try:
        h, m = data.split(":", 1)
        h = int(h)
        m = int(m)
        datetime.datetime.now().replace(hour=h, minute=m)
        context.user_data["end_time"] = (h, m)
    except ValueError:
        raise IncorrectInputDataError()

    await update.message.reply_text(f'Сколько слотов? (0 -- не ограничено)')
    return WAITING_SLOT


async def request_delivery(update: Update, context: CallbackContext):
    try:
        context.user_data["slot"] = int(update.message.text)
    except ValueError:
        raise IncorrectInputDataError()
    await update.message.reply_text(f'Во сколько будет выдача заказов?')
    return WAITING_DELIVERY


async def get_money(update: Update, context: CallbackContext):
    data = update.message.text.strip()
    context.user_data["order_time"] = data

    await update.message.reply_text(f"Введите информацию кому скидывать за праздник.")
    return WAITING_MONEY


async def get_all_data(update: Update, context: CallbackContext):
    data = update.message.text.strip()
    context.user_data["money_msg"] = data
    return await create_event(update, context, update.message.from_user.id)


async def create_event(update: Update, context: CallbackContext, owner_id: int):
    h, m = context.user_data["end_time"]
    slot = context.user_data["slot"]
    order_time_data = context.user_data["order_time"]
    menu_id = context.user_data["menu_id"]
    money_msg = context.user_data.get("money_msg")

    s = Storage()

    if slot > 0:
        text = (
            f"Сбор заказов до {h:02}:{m:02} или до {slot} позиций.\nВыдача заказов: {order_time_data}"
        )
    else:
        text = (
            f"Сбор заказов до {h:02}:{m:02}\nВыдача заказов: {order_time_data}"
        )

    if update.message:
        chat_id = update.message.chat_id
    elif update.callback_query:
        chat_id = update.callback_query.message.chat_id
    else:
        raise BaseBotException()

    order_message = await context.bot.send_message(
        chat_id=chat_id,
        text=text
    )

    additional_message = await context.bot.send_message(
        chat_id=chat_id,
        text="Опроса больше нет. Действия с заказом доступны по кнопкам."
    )

    dt = datetime.datetime.now().replace(hour=h, minute=m, second=0)

    admin_message = await context.bot.send_message(
        chat_id=owner_id,
        text="Админское сообщение!"
    )

    async with s:
        event = await s.event.create(
            chat_id=chat_id,
            owner_id=owner_id,
            admin_message_id=admin_message.message_id,
            order_message_id=order_message.message_id,
            additional_message_id=additional_message.message_id,
            collect_message_id=None,
            menu_id=menu_id,
            available_slots=slot,
            delivery_info=order_time_data,
            order_end_time=dt,
            money_message=money_msg
        )

    login = LoginUrl(f"{context.bot_data['base_url']}login?event_id={event.id}")
    keyboard = [
        [
            InlineKeyboardButton("Заказать", login_url=login)
        ],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await order_message.edit_reply_markup(markup)

    keyboard = [
        [
            InlineKeyboardButton("Отменить заказ", callback_data=f"order_cancel_{event.id}"),
            InlineKeyboardButton("Мне повезёт!", callback_data=f"order_lucky_{event.id}"),
        ],
        [
            InlineKeyboardButton("Мне как прошлый раз", callback_data=f"order_repeat_{event.id}"),
        ],
        [
            InlineKeyboardButton("Посмотреть мой заказ", callback_data=f"order_show_{event.id}")
        ],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await additional_message.edit_reply_markup(markup)

    try:
        # pin and edit_reply_markup leads to crash on some platforms
        time.sleep(1)
        await order_message.pin()
    except TelegramError:
        pass

    job_context = dict(
        event_id=event.id
    )

    context.job_queue.run_once(close_poll_job, dt - datetime.datetime.now(), chat_id=order_message.chat_id,
                               context=job_context, name=f"{order_message.chat_id}")

    return ConversationHandler.END


async def close_poll_job(context: CallbackContext):
    job_context = context.job.context
    s = Storage()
    await close_poll_if_necessary(s, context.bot, job_context["event_id"], force=True)


launch_handler = ConversationHandler(
    entry_points=[
        CommandHandler("launch", launch, filters.ChatType.GROUPS),
        MessageHandler(filters.Text(["Начинаем шавадей", "Начинаем шавадэй"]) & filters.ChatType.GROUPS, launch)
    ],
    states={
        WAITING_REPEAT: [CallbackQueryHandler(repeat_previous_callback, pattern="repeat_answer_")],
        WAITING_MENU_CALLBACK: [CallbackQueryHandler(request_menu_callback, pattern="menu_start_")],
        WAITING_TIME: [MessageHandler(filters.TEXT, request_slot)],
        WAITING_SLOT: [MessageHandler(filters.TEXT, request_delivery)],
        WAITING_DELIVERY: [MessageHandler(filters.TEXT, get_money)],
        WAITING_MONEY: [MessageHandler(filters.TEXT, get_all_data)]
    },
    fallbacks=[cancel_handler]
)