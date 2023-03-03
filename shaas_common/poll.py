import datetime
import logging
import time
from typing import List

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError, BadRequest
from telegram.ext import CallbackContext
from telegram.helpers import mention_markdown

from shaas_common.model.event.orm import Event, EventState
from shaas_common.storage import Storage


async def check_poll_exceeded(s: Storage, event) -> bool:
    if event.available_slots <= 0:
        return False

    current_orders = await s.order.get_order_total(event.id)

    return current_orders >= event.available_slots


async def close_events_if_necessary(context: CallbackContext):
    s = Storage()

    async with s:
        events: List[Event] = await s.event.get_active()

        for event in events:
            logging.info(f"Event {event.id} -> {event.order_end_time}")
            if event.order_end_time > datetime.datetime.now():
                if await check_poll_exceeded(s, event) is False:
                    continue

            logging.info(f"Event {event.id} is about to close")

            order_entries = await s.order.get_order_list(event.id)
            order_list = await s.order.get_order_comments(event.id)

            order_entries_dict = dict()
            for _, item, count in order_entries:
                if item not in order_entries_dict:
                    order_entries_dict[item] = 0
                order_entries_dict[item] += count
            order_entries_str = "\n".join([f"{count}x {item.name}" for item, count in order_entries_dict.items()])

            comment_list_str = []
            for order in order_list:
                member = await context.bot.getChatMember(event.chat_id, order.user_id)
                mention = mention_markdown(order.user_id, member.user.full_name)

                comment_str = f"{mention} заказал:\n"
                for order_id, item, count in order_entries:
                    if order_id != order.id:
                        continue
                    comment_str += f"{count}x {item.name}\n"
                comment_safe = order.comment.replace("\n", "").strip()
                comment_str += "c комментарием:\n" + comment_safe + "\n"
                comment_list_str.append(comment_str)


            order_text = (
                "Заказ:\n" + order_entries_str
            )
            if len(comment_list_str):
                order_text += (
                    "\n\n" +
                    "Комментарии:\n" +
                    "\n".join(comment_list_str)
                )
            logging.info(order_text)
            try:
                await context.bot.delete_message(
                    chat_id=event.chat_id,
                    message_id=event.additional_message_id
                )
            except:
                pass

            try:
                await context.bot.edit_message_reply_markup(
                    chat_id=event.chat_id,
                    message_id=event.order_message_id
                )
            except BadRequest:
                pass

            time.sleep(1)

            try:
                await context.bot.unpin_chat_message(
                    chat_id=event.chat_id,
                    message_id=event.order_message_id
                )
            except TelegramError:
                pass

            keyboard = [
                [InlineKeyboardButton("Я забрал", callback_data=f"order_taken_{event.id}")]
            ]
            markup = InlineKeyboardMarkup(keyboard)

            text = "Прием заказов окончен!\nКак только получите свой заказ -- жмите кнопку!"
            if event.money_message:
                text += f"\n\n{event.money_message}"

            message = await context.bot.send_message(
                chat_id=event.chat_id,
                text=text,
                reply_markup=markup
            )

            await s.event.update(
                event.id,
                collect_message_id=message.message_id,
                state=EventState.delivery
            )

            try:
                await message.pin()
            except TelegramError:
                pass

            await context.bot.send_message(
                chat_id=event.chat_id,
                text=order_text,
                parse_mode="markdown"
            )
