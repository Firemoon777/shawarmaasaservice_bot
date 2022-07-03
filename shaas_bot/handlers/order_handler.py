import time

from sqlalchemy import select, update as sql_update
from telegram import Update
from telegram.ext import CallbackContext, CallbackQueryHandler

from shaas_common.model import Order, Event, EventState
from shaas_common.session import SessionLocal


async def order_callback(update: Update, context: CallbackContext):
    event_id = int(update.callback_query.data.replace("order_taken_", ""))
    user_id = update.callback_query.from_user.id

    session = SessionLocal()

    q = select(Event).where(Event.id == event_id)
    result = await session.execute(q)
    event = list(result.scalars())

    if not event:
        await update.callback_query.answer()
        return

    event = event[0]

    q = sql_update(Order).where(Order.event_id == event_id, Order.user_id == user_id).values(is_taken=True)
    await session.execute(q)
    await session.commit()

    await update.callback_query.answer(text="Принято")

    q = select(Order.is_taken).where(Order.event_id == event_id)
    result = await session.execute(q)
    if not all(result.scalars()):
        return

    await context.bot.unpin_chat_message(
        chat_id=event.chat_id,
        message_id=event.collect_message_id
    )

    time.sleep(1)

    await context.bot.edit_message_reply_markup(
        chat_id=event.chat_id,
        message_id=event.collect_message_id,
        reply_markup=None
    )

    await context.bot.send_message(
        chat_id=event.chat_id,
        text="Все отметились, что забрали заказ"
    )

    event.state = EventState.finished
    await session.commit()

order_callback_handler = CallbackQueryHandler(order_callback, pattern="order_taken_")
