import datetime
import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, \
    filters

from shaas_bot.utils import is_group_chat, is_sender_admin, cancel_handler
from shaas_common.exception.bot import IncorrectInputDataError, NoMenuInGroupError, AlreadyRunningError, BaseBotException, \
    NoItemsInMenuError
from shaas_common.poll import close_poll_if_necessary
from shaas_common.storage import Storage

WAITING_REPEAT = 0
WAITING_MENU_CALLBACK = 1
WAITING_TIME = 2
WAITING_SLOT = 3
WAITING_DELIVERY =4


async def launch(update: Update, context: CallbackContext):
    await is_group_chat(update, context, raises=True)
    await is_sender_admin(update, context, raises=True)

    s = Storage()

    if await s.event.get_current(update.message.chat_id):
        raise AlreadyRunningError()

    context.user_data.clear()

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

    return await create_poll(update, context)


async def request_menu(update: Update, context: CallbackContext, s: Storage):
    if update.message:
        chat_id = update.message.chat_id
    elif update.callback_query:
        chat_id = update.callback_query.message.chat_id
    else:
        raise BaseBotException()

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


async def get_all_data(update: Update, context: CallbackContext):
    data = update.message.text.strip()
    context.user_data["order_time"] = data
    return await create_poll(update, context)


async def create_poll(update: Update, context: CallbackContext):
    h, m = context.user_data["end_time"]
    slot = context.user_data["slot"]
    order_time_data = context.user_data["order_time"]
    menu_id = context.user_data["menu_id"]

    s = Storage()

    if slot > 0:
        question = (
            f"Что заказывать будете?\n"
            f"Сбор заказов до {h:02}:{m:02} или до {slot} позиций.\nВыдача заказов: {order_time_data}"
        )
    else:
        question = (
            f"Что заказывать будете?\n"
            f"Сбор заказов до {h:02}:{m:02}\nВыдача заказов: {order_time_data}"
        )

    if update.message:
        chat_id = update.message.chat_id
    elif update.callback_query:
        chat_id = update.callback_query.message.chat_id
    else:
        raise BaseBotException()

    items = await s.menu_item.get_items_for_poll(menu_id)
    if len(items) == 0:
        raise NoItemsInMenuError()
    items = items[:9]
    skip_option = len(items)
    options = [item.name for item in items] + ["Мне бы кнопку жамкнуть"]
    options_id = [item.id for item in items]

    message = await context.bot.sendPoll(
        chat_id=chat_id,
        question=question,
        options=options,
        is_anonymous=False,
        allows_multiple_answers=True
    )

    dt = datetime.datetime.now().replace(hour=h, minute=m, second=0)

    event = await s.event.create(
        chat_id=chat_id,
        poll_message_id=message.message_id,
        poll_id=message.poll.id,
        collect_message_id=None,
        skip_option=skip_option,
        poll_options=options_id,
        menu_id=menu_id,
        available_slots=slot,
        delivery_info=order_time_data,
        order_end_time=dt
    )

    await s.commit()

    keyboard = [
        [
            InlineKeyboardButton("Заказать", url=f"https://t.me/{context.bot.username}?start={menu_id}_{chat_id}")
        ],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await message.edit_reply_markup(markup)

    try:
        # pin and edit_reply_markup leads to crash on some platforms
        time.sleep(1)
        await message.pin()
    except TelegramError:
        pass

    job_context = dict(
        poll_id=event.poll_id
    )

    context.job_queue.run_once(close_poll_job, dt - datetime.datetime.now(), chat_id=message.chat_id,
                               context=job_context, name=f"{message.chat_id}")

    return ConversationHandler.END


async def close_poll_job(context: CallbackContext):
    job_context = context.job.context
    s = Storage()
    await close_poll_if_necessary(s, context.bot, poll_id=job_context["poll_id"], force=True)


launch_handler = ConversationHandler(
    entry_points=[CommandHandler("launch", launch, filters.ChatType.GROUPS)],
    states={
        WAITING_REPEAT: [CallbackQueryHandler(repeat_previous_callback, pattern="repeat_answer_")],
        WAITING_MENU_CALLBACK: [CallbackQueryHandler(request_menu_callback, pattern="menu_start_")],
        WAITING_TIME: [MessageHandler(filters.TEXT, request_slot)],
        WAITING_SLOT: [MessageHandler(filters.TEXT, request_delivery)],
        WAITING_DELIVERY: [MessageHandler(filters.TEXT, get_all_data)]
    },
    fallbacks=[cancel_handler]
)