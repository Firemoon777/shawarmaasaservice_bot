import time

from sqlalchemy import select, func
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError

from shaas_common.model import Event, EventState, Order, MenuItem, OrderComment
from shaas_common.session import SessionLocal


async def check_poll_exceeded(session: SessionLocal, event) -> bool:
    if event.available_slots <= 0:
        return False

    current_orders = await Order.get_sum(session, event.id)

    return current_orders >= event.available_slots


async def close_poll_if_necessary(session: AsyncSession, bot: Bot, poll_id, force=False):
    event = await Event.get_by_poll(session, poll_id)
    if not event:
        return

    if event.state != EventState.collecting_orders:
        return

    if not force and await check_poll_exceeded(session, event) is False:
        return

    q = select([MenuItem.name, func.sum(Order.count)]).join(MenuItem).where(Order.event_id == event.id).group_by(MenuItem.name)
    result: Result = await session.execute(q)
    order_list = []
    for name, count in result.fetchall():
        order_list.append(f"{count}x {name}")

    q = select(OrderComment.comment).where(OrderComment.event_id == event.id)
    result: Result = await session.execute(q)
    comment_list = []
    for comment in list(result.scalars()):
        comment_safe = comment.replace("\n", "").strip()
        comment_list.append(f"- {comment_safe}")

    order_text = (
        "Заказ:\n" +
        "\n".join(order_list) + "\n"
    )
    if len(comment_list):
        order_text +=  (
            "\n" +
            "Комментарии:\n" +
            "\n".join(comment_list)
        )

    await bot.stop_poll(
        chat_id=event.chat_id,
        message_id=event.poll_message_id
    )

    time.sleep(1)

    try:
        await bot.unpin_chat_message(
            chat_id=event.chat_id,
            message_id=event.poll_message_id
        )
    except TelegramError:
        pass

    keyboard = [
        [InlineKeyboardButton("Я забрал", callback_data=f"order_taken_{event.id}")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    message = await bot.send_message(
        chat_id=event.chat_id,
        text="Прием заказов окончен!\n\nКак только получите свой заказ -- жмите кнопку!",
        reply_markup=markup
    )
    event.collect_message_id = message.message_id
    event.state = EventState.delivery

    try:
        await message.pin()
    except TelegramError:
        pass

    await bot.send_message(
        chat_id=event.chat_id,
        text=order_text
    )

    await session.commit()
