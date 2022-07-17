import time
from typing import List, Tuple

from sqlalchemy import select, update as sql_update
from telegram import Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler

from shaas_common.model import Order, Event, EventState, MenuItem
from shaas_common.session import SessionLocal


async def order_list(update: Update, context: CallbackContext):
    session = SessionLocal()
    active = await Event.is_active(session, update.message.chat_id)

    if not active:
        await update.message.reply_text("Нет активных событий")
        return

    if active.state == EventState.collecting_orders:
        await update.message.reply_text("Заказы только собираются, потерпите")
        return

    q = (
        select(Order.user_id, Order.count, MenuItem.name)
            .join(MenuItem)
            .where(Order.event_id == active.id, Order.is_taken == False)
    )
    result = await session.execute(q)
    result_list: List[Tuple] = list(result.fetchall())

    output = dict()
    for entry in result_list:
        if entry[0] not in output:
            output[entry[0]] = []

        output[entry[0]].append(f"{entry[1]}x {entry[2]}")

    msg = []
    for user_id, order_list in output.items():
        text = ""
        member = await context.bot.get_chat_member(chat_id=update.message.chat_id, user_id=user_id)
        if member.user.username:
            text += "@" + member.user.username + ":\n"
        else:
            text += member.user.full_name + ":\n"

        text += "\n".join(order_list)
        msg.append(text)

    await update.message.reply_text(text="\n\n".join(msg))


order_list_handler = CommandHandler("list", order_list)