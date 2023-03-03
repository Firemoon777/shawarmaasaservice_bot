import random
import time

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CallbackQueryHandler

from shaas_common.billing import get_short_price_message, get_html_price_message
from shaas_common.model import EventState, Event, MenuItem
from shaas_common.storage import Storage


async def order_taken_callback(update: Update, context: CallbackContext):
    event_id = int(update.callback_query.data.replace("order_taken_", ""))
    user_id = update.callback_query.from_user.id

    await order_show_callback(update, context)

    s = Storage()

    async with s:

        event: Event = await s.event.get(event_id)

        await s.order.take_order(event_id, user_id)

        await context.bot.send_message(chat_id=user_id, text=event.money_message)

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
                text="Все отметились, что забрали заказ\n\n" + event.money_message
            )

            await s.event.update(
                event.id,
                state=EventState.finished
            )


order_taken_handler = CallbackQueryHandler(order_taken_callback, pattern="order_taken_")


async def order_repeat_callback(update: Update, context: CallbackContext):
    current_event_id = int(update.callback_query.data.replace("order_repeat_", ""))
    user_id = update.callback_query.from_user.id

    s = Storage()

    async with s:
        event = await s.event.get(current_event_id)

        if not event:
            await update.callback_query.answer()
            return

        previous_order = await s.order.get_previous_order(user_id)
        user_order_list = await s.order.get_order_list(previous_order.event_id, user_id)

    if not user_order_list:
        await update.callback_query.answer(
            text="Прошлый раз вы ничего не заказывали.",
            show_alert=True,
        )
        return

    msg = "Ваш заказ:\n"
    for _, item, count in user_order_list:
        msg += f"\n{count}x {item.name}"

    async with s:

        comment = await s.order.get_comment(event.id, user_id)
        if comment:
            msg += f"\n\nКомментарий:\n{comment}"

        await s.order.create_order(
            update.callback_query.from_user.id,
            event.id,
            {k:v for _, k, v in user_order_list},
            comment
        )

    try:
        await update.callback_query.answer(text=msg, show_alert=True)
    except BadRequest:
        await context.bot.send_message(
            chat_id=update.callback_query.from_user.id,
            text=f"Ваш заказ настолько большой что не влезает в уведолмение.\n\n{msg}",
        )

order_repeat_handler = CallbackQueryHandler(order_repeat_callback, pattern="order_repeat_")


async def order_lucky_callback(update: Update, context: CallbackContext):
    current_event_id = int(update.callback_query.data.replace("order_lucky_", ""))
    user_id = update.callback_query.from_user.id

    s = Storage()

    async with s:
        event: Event = await s.event.get(current_event_id)
        menu = await s.menu_item.get_items(event.menu_id)

        if not event:
            await update.callback_query.answer()
            return

        lucky_item: MenuItem = random.choice(menu)

        msg = f"Ваш заказ на сегодня:\n1x {lucky_item.name} - {lucky_item.price} р."

        await s.order.create_order(
            user_id,
            event.id,
            {lucky_item: 1}
        )

    await update.callback_query.answer(text=msg, show_alert=True)

order_lucky_handler = CallbackQueryHandler(order_lucky_callback, pattern="order_lucky_")


async def order_show_callback(update: Update, context: CallbackContext):
    event_id = int(update.callback_query.data.split("_")[2])
    user_id = update.callback_query.from_user.id

    s = Storage()

    async with s:
        event = await s.event.get(event_id)

        if not event:
            await update.callback_query.answer(text="Такого события нет")
            return

        user_order_list = await s.order.get_order_list(event.id, user_id)
        comment = await s.order.get_comment(event_id, user_id)

    order_data = {item: count for _, item, count in user_order_list}

    if not user_order_list:
        await update.callback_query.answer(
            text="Вы ничего не заказали. Это грустно.",
            show_alert=True,
        )
        return

    msg = "Ваш заказ:\n" + get_short_price_message(order_data, comment)

    try:
        await update.callback_query.answer(text=msg, show_alert=True)
    except BadRequest:
        msg = "Ваш заказ:\n\n" + get_html_price_message(order_data, comment)
        await context.bot.send_message(
            chat_id=update.callback_query.from_user.id,
            text=msg,
            parse_mode="html"
        )
        await update.callback_query.answer(
            text="Ваш заказ настолько большой что не влезает в уведолмение, поэтому был отправлен сообщением."
        )

order_show_handler = CallbackQueryHandler(order_show_callback, pattern="order_show_")


async def order_cancel_callback(update: Update, context: CallbackContext):
    event_id = int(update.callback_query.data.replace("order_cancel_", ""))
    user_id = update.callback_query.from_user.id

    s = Storage()

    async with s:
        event = await s.event.get(event_id)

        if not event:
            await update.callback_query.answer(text="Такого события нет")
            return

        await s.order.cancel_order(user_id, event.id)

    await update.callback_query.answer(text="Заказ отменен.", show_alert=True)

order_cancel_handler = CallbackQueryHandler(order_cancel_callback, pattern="order_cancel_")