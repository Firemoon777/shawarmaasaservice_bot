import csv
import datetime
import random
import time
from io import StringIO, BytesIO
from typing import Tuple, List, Dict

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CallbackQueryHandler

from shaas_common.billing import get_short_price_message, get_html_price_message
from shaas_common.model import EventState, Event, MenuItem, Chat
from shaas_common.notification import Notification
from shaas_common.storage import Storage

import matplotlib.pyplot as plt
import numpy as np


async def order_taken_callback(update: Update, context: CallbackContext):
    event_id = int(update.callback_query.data.replace("order_taken_", ""))
    user_id = update.callback_query.from_user.id

    await order_show_callback(update, context)

    s = Storage()

    async with s:

        event: Event = await s.event.get(event_id)
        user: Chat = await s.chat.get(user_id)

        await s.order.take_order(event_id, user_id)

        try:
            await Notification(user, context.bot).send_message(event.money_message)
        except Exception as e:
            pass

        result = await s.order.get_pending(event_id)

        if not result:
            # stat_chat_id = -1001569537280
            # # stat_chat_id = event.chat_id
            # year_usage: List[MenuItem, int] = await s.order.get_current_year_statistic(stat_chat_id)
            # year_usage.sort(key=lambda x: x[1], reverse=True)
            # print(year_usage)
            #
            # year_event_usage: Dict[str, List[Tuple[MenuItem, int]]] = await s.order.get_current_year_statistic_for_all_events(stat_chat_id)
            #
            # labels = []
            # items_name = [item.name for item, _ in year_usage]
            # counts = {
            #     name: list() for name in items_name
            # }
            #
            # ylim = 0
            # for d, items in year_event_usage.items():
            #     tmp = 0
            #
            #     labels.append(d)
            #     for name in items_name:
            #         counts[name].append(0)
            #
            #     for item, count in items:
            #         counts[item.name][-1] = count
            #         tmp += count
            #     ylim = max(ylim, tmp)
            #
            # width = 0.6  # the width of the bars: can also be len(x) sequence
            # bottom = np.zeros(len(labels))
            #
            # fig, ax = plt.subplots(figsize=(8, 4.5), dpi=150)
            # for item_name, item_count in counts.items():
            #     p = ax.bar(
            #         labels,
            #         item_count,
            #         width,
            #         label=item_name,
            #         bottom=bottom,
            #
            #     )
            #     bottom += item_count
            #
            #     # ax.bar_label(p, label_type='center')
            #
            # ax.set_ylim(0, ylim + 10)
            # for tick in ax.get_xticklabels():
            #     tick.set_rotation(90)
            #
            # box = ax.get_position()
            # ax.set_position([box.x0, box.y0 + 0.1, box.width * 0.75, box.height-0.1])
            #
            # # Put a legend to the right of the current axis
            # ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
            #
            # ax.set_title('Статистика')
            # ax.grid(axis="y")
            # ax.text(0, 123, 123, ha='center', weight='bold', color='black')
            # ax.text(1, 4567, 4567, ha='center', weight='bold', color='black')
            #
            # buf = BytesIO()
            # plt.savefig(buf, format="png")
            # buf.seek(0)
            #
            # await context.bot.send_photo(
            #     chat_id=event.chat_id,
            #     photo=buf,
            #     caption="Все отметились, что забрали заказ\n\n" + event.money_message,
            #     disable_notification=True
            # )
            #
            # return
            total = await s.order.get_order_list_extended(event.id)

            today = f"{event.order_end_time.year}-{event.order_end_time.month:02}-{event.order_end_time.day:02}"
            string_io = StringIO()
            fieldnames = ["sum", "date", "login", "user_id", "name"]
            writer = csv.DictWriter(string_io, fieldnames=fieldnames)
            writer.writeheader()
            for order, chat, item_sum in total:
                writer.writerow({
                    "sum": item_sum,
                    "date": str(today),
                    "login": chat.username,
                    "user_id": chat.id,
                    "name": chat.name
                })

            await context.bot.send_document(
                event.owner_id,
                document=string_io.getvalue().encode("utf-8"),
                filename=f"{today}-shaas-{event.id}.csv"
            )

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

            ## Тут сбщ

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
        event: Event = await s.event.get(current_event_id)
        user: Chat = await s.chat.get(user_id)

        if not event:
            await update.callback_query.answer()
            return

        previous_order = await s.order.get_previous_order(
            user_id,
            current_event_id=event.id,
            current_chat_id=event.chat_id
        )
        user_order_list = await s.order.get_order_list(previous_order.event_id, user_id)
        comment = await s.order.get_comment(event.id, user_id)

    if not user_order_list:
        await update.callback_query.answer(
            text="Прошлый раз вы ничего не заказывали.",
            show_alert=True,
        )
        return

    new_user_order_list = {}
    for _, item, count in user_order_list:
        if item.id == 0:
            continue

        new_user_order_list[item] = count

    async with s:
        await s.order.create_order(
            update.callback_query.from_user.id,
            event.id,
            new_user_order_list,
            comment
        )

    try:
        msg = "Ваш заказ:\n\n" + get_short_price_message(new_user_order_list, comment)
        await update.callback_query.answer(text=msg, show_alert=True)
    except BadRequest:
        pass
    finally:
        msg = "Ваш заказ:\n\n" + get_html_price_message(new_user_order_list, comment)
        await Notification(user, context.bot).send_message(msg)

order_repeat_handler = CallbackQueryHandler(order_repeat_callback, pattern="order_repeat_")


async def order_lucky_callback(update: Update, context: CallbackContext):
    current_event_id = int(update.callback_query.data.replace("order_lucky_", ""))
    user_id = update.callback_query.from_user.id

    s = Storage()

    async with s:
        event: Event = await s.event.get(current_event_id)
        user: Chat = await s.chat.get(user_id)
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

    await Notification(user, context.bot).send_message(msg)

order_lucky_handler = CallbackQueryHandler(order_lucky_callback, pattern="order_lucky_")


async def order_show_callback(update: Update, context: CallbackContext):
    event_id = int(update.callback_query.data.split("_")[2])
    user_id = update.callback_query.from_user.id

    s = Storage()

    async with s:
        event = await s.event.get(event_id)
        user: Chat = await s.chat.get(user_id)

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
        await Notification(user, context.bot).send_message(msg, parse_mode="html")
        await update.callback_query.answer(
            text="Ваш заказ настолько большой что не влезает в уведолмение."
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