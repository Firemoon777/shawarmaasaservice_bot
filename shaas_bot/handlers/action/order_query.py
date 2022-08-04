import time

from telegram import Update
from telegram.ext import CallbackContext, CallbackQueryHandler

from shaas_common.model import EventState
from shaas_common.poll import close_poll_if_necessary
from shaas_common.storage import Storage


async def order_taken_callback(update: Update, context: CallbackContext):
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
    for item, count in user_order_list:
        msg += f"\n{count}x {item.name}"

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

order_taken_handler = CallbackQueryHandler(order_taken_callback, pattern="order_taken_")


async def order_repeat_callback(update: Update, context: CallbackContext):
    current_event_id = int(update.callback_query.data.replace("order_repeat_", ""))
    user_id = update.callback_query.from_user.id

    s = Storage()

    event = await s.event.get(current_event_id)

    if not event:
        await update.callback_query.answer()
        return

    previous_event = await s.event.get_last_finished(update.callback_query.message.chat_id)
    user_order_list = await s.order.get_order_list(previous_event.id, user_id)

    if not user_order_list:
        await update.callback_query.answer(
            text="Прошлый раз вы ничего не заказывали. Увы, но пока это работает только на предыдущее событие.",
            show_alert=True,
        )
        return

    msg = "Ваш заказ:\n"
    for item, count in user_order_list:
        msg += f"\n{count}x {item.name}"

    comment = await s.order.get_comment(event.id, user_id)
    if comment:
        msg += f"\n\nКомментарий:\n{comment}"

    await s.order.create_order(
        update.callback_query.from_user.id,
        event.id,
        {k:v for k, v in user_order_list}
    )
    await s.commit()

    await update.callback_query.answer(text=msg, show_alert=True)

    await close_poll_if_necessary(s, context.bot, event.id)

order_repeat_handler = CallbackQueryHandler(order_repeat_callback, pattern="order_repeat_")


async def order_show_callback(update: Update, context: CallbackContext):
    event_id = int(update.callback_query.data.replace("order_show_", ""))
    user_id = update.callback_query.from_user.id

    s = Storage()

    event = await s.event.get(event_id)

    if not event:
        await update.callback_query.answer(text="Такого события нет")
        return

    user_order_list = await s.order.get_order_list(event.id, user_id)
    if not user_order_list:
        await update.callback_query.answer(
            text="Вы ничего не заказали. Это грустно.",
            show_alert=True,
        )
        return

    msg = "Ваш заказ:\n"
    for item, count in user_order_list:
        msg += f"\n{count}x {item.name}"

    comment = await s.order.get_comment(event_id, user_id)
    if comment:
        msg += f"\n\nКомментарий:\n{comment}"

    await update.callback_query.answer(text=msg, show_alert=True)

order_show_handler = CallbackQueryHandler(order_show_callback, pattern="order_show_")


async def order_cancel_callback(update: Update, context: CallbackContext):
    event_id = int(update.callback_query.data.replace("order_cancel_", ""))
    user_id = update.callback_query.from_user.id

    s = Storage()

    event = await s.event.get(event_id)

    if not event:
        await update.callback_query.answer(text="Такого события нет")
        return

    await s.order.cancel_order(user_id, event.id)
    await s.commit()

    await update.callback_query.answer(text="Заказ отменен.", show_alert=True)

order_cancel_handler = CallbackQueryHandler(order_cancel_callback, pattern="order_cancel_")