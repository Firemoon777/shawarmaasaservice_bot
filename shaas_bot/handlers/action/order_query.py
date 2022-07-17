import time

from telegram import Update
from telegram.ext import CallbackContext, CallbackQueryHandler

from shaas_common.model import EventState
from shaas_common.storage import Storage


async def order_callback(update: Update, context: CallbackContext):
    event_id = int(update.callback_query.data.replace("order_taken_", ""))
    user_id = update.callback_query.from_user.id

    s = Storage()

    event = await s.event.get(event_id)

    if not event:
        await update.callback_query.answer()
        return

    await s.order.take_order(event_id, user_id)
    user_order_list = await s.order.get_order_list(event_id, user_id)
    msg = "Ваш заказ:\n"
    for entry, count in user_order_list:
        msg += f"\n{count}x {entry}"

    await update.callback_query.answer(text=msg, show_alert=True)

    result = await s.order.get_pending(event_id)
    if not result:
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
    await s.commit()

order_callback_handler = CallbackQueryHandler(order_callback, pattern="order_taken_")