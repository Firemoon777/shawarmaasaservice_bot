import time

from sqlalchemy import select, func
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from telegram.helpers import mention_markdown

from shaas_common.model import MenuItem
from shaas_common.model.event.orm import Event, EventState
from shaas_common.model.order.orm import Order
from shaas_common.session import SessionLocal
from shaas_common.storage import Storage


async def check_poll_exceeded(s: Storage, event) -> bool:
    if event.available_slots <= 0:
        return False

    current_orders = await s.order.get_order_total(event.id)

    return current_orders >= event.available_slots


class OrderComment(object):
    pass


async def close_poll_if_necessary(s: Storage, bot: Bot, event_id, force=False):
    async with s:
        event = await s.event.get(event_id)

        if not event:
            return

        if event.state != EventState.collecting_orders:
            return

        if not force and await check_poll_exceeded(s, event) is False:
            return

        order_entries = await s.order.get_order_list(event.id)
        order_list = await s.order.get_order_comments(event.id)

        order_entries_str = []
        for _, item, count in order_entries:
            order_entries_str.append(f"{count}x {item.name}")

        comment_list_str = []
        for order in order_list:
            for order_id, item, count in order_entries:
                if order_id != order.id:
                    continue

                member = await bot.getChatMember(event.chat_id, order.user_id)
                mention = mention_markdown(order.user_id, member.user.full_name)

                comment_str = f"{mention} заказал:"
                for _, item, count in order_entries:
                    comment_str += f"{count}x {item.name}\n"
                comment_safe = order.comment.replace("\n", "").strip()
                comment_str += "c комментарием:\n" + comment_safe + "\n"
                comment_list_str.append(comment_str)
                break

        order_text = (
            "Заказ:\n" +
            "\n".join(order_entries_str) + "\n"
        )
        if len(comment_list_str):
            order_text +=  (
                "\n" +
                "Комментарии:\n" +
                "\n".join(comment_list_str)
            )

        await bot.delete_message(
            chat_id=event.chat_id,
            message_id=event.additional_message_id
        )

        await bot.edit_message_reply_markup(
            chat_id=event.chat_id,
            message_id=event.order_message_id
        )

        time.sleep(1)

        try:
            await bot.unpin_chat_message(
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

        message = await bot.send_message(
            chat_id=event.chat_id,
            text=text,
            reply_markup=markup
        )

        await s.event.update(
            event.id,
            collect_message_id = message.message_id,
            state = EventState.delivery
        )

        try:
            await message.pin()
        except TelegramError:
            pass

        await bot.send_message(
            chat_id=event.chat_id,
            text=order_text,
            parse_mode="markdown"
        )
