import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from telegram.ext import CallbackContext

from shaas.const import product
from shaas.storage import storage_init_with_poll
from shaas.utils import get_orders


async def send_forbidden(update: Update, context: CallbackContext):
    await update.message.reply_text(
        f"Действие доступно только администраторам.\n\nА вы не администратор."
    )


async def send_poll_is_running(update: Update, context: CallbackContext):
    await update.message.reply_text(
        f"Шавадей ещё не закончился!"
    )


async def send_picked_up(update: Update, context: CallbackContext):
    await update.callback_query.message.reply_text(
        f"Все отметились, что забрали заказы!"
    )


async def send_incorrect_input(update: Update, context: CallbackContext):
    await update.message.reply_text(f"Некорректный ввод, попробуйте снова")


async def ask_vote_timeout(update: Update, context: CallbackContext):
    dt = datetime.datetime.now()
    await update.message.reply_text(
        f'Время начинать шавадэй!\n'
        f'\n'
        f'До какого времени активно голосование?\n'
        f'Введи в формате HH:MM, например, 13:15\n'
        f'\n'
        f'Время бота: {dt.hour:02}:{dt.minute:02}'
    )


async def ask_order_time(update: Update, context: CallbackContext):
    await update.message.reply_text(f'Во сколько будет выдача заказов?')


async def ask_slots(update: Update, context: CallbackContext):
    await update.message.reply_text(f'Сколько слотов? (0 -- не ограничено)')


async def create_poll(update: Update, context: CallbackContext):
    h, m = context.user_data["end_time"]
    slot = context.user_data["slot"]
    order_time_data = context.user_data["order_time"]

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

    message = await context.bot.sendPoll(
        chat_id=update.message.chat_id,
        question=question,
        options=[
            "Турецкая",
            "Иранская",
            "Сирийская",
            "Ливанская",
            "Иорданская",
            "Марокканская",
            "Алжирская",
            "Дурум кебаб",
            "Фалафель",
            "Мне бы кнопку жамкнуть"
        ],
        is_anonymous=False,
        allows_multiple_answers=True
    )
    dt = datetime.datetime.now().replace(hour=h, minute=m, second=0)
    job_context = dict(
        message_id=message.message_id,
        chat_id=message.chat_id
    )

    storage_init_with_poll(context, message, slot)

    context.job_queue.run_once(close_poll_job, dt - datetime.datetime.now(), chat_id=message.chat_id,
                               context=job_context, name=f"{message.chat_id}")


async def send_scheduled_reply(context: CallbackContext, chat_id, message_id):
    keyboard = [
        [InlineKeyboardButton('Я забрал', callback_data="pickup")]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    msg = await context.bot.send_message(
        chat_id=chat_id,
        reply_to_message_id=message_id,
        text="Прием заказов окончен!\n"
             "\n"
             "Как только получите свой заказ -- жмите кнопку!",
        reply_markup=markup
    )

    orders = {i:0 for i in range(9)}
    for user_id, user_data in context.bot_data[chat_id]["users"].items():
        for option in user_data["options"]:
            orders[option] += 1
    positions = []
    for i, count in orders.items():
        if count > 0:
            positions.append(f"{product[i]}: {count}")
    await context.bot.send_message(
        chat_id=chat_id,
        reply_to_message_id=message_id,
        text="\n".join(positions)
    )

    await msg.pin()


async def close_poll(context: CallbackContext, chat_id, message_id):
    try:
        await context.bot.stop_poll(
            chat_id=chat_id,
            message_id=message_id
        )
    except TelegramError:
        return

    await send_scheduled_reply(context, chat_id, message_id)
    context.bot_data[chat_id]["is_running"] = False


async def close_poll_job(context: CallbackContext):
    job_context = context.job.context
    await close_poll(context, job_context["chat_id"], job_context["message_id"])
