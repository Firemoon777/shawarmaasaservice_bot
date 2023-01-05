import datetime
import hmac
import hashlib
import uuid
from typing import Optional, List, Dict

from fastapi import APIRouter, Depends, Cookie, Form, File, UploadFile, HTTPException
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import Response
from telegram import LoginUrl, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application
from telegram.helpers import mention_markdown

from shaas_common.model import Token, Event, MenuItem, EventState
from shaas_common.security import is_token_valid
from shaas_common.storage import Storage
from shaas_web.bot import get_bot

control_router = APIRouter(prefix="/control")


@control_router.get("/{event_id}")
async def check(event_id:int, shaas_token: Optional[str] = Cookie(default=None, alias="token")):
    token: Token = await is_token_valid(shaas_token)

    s = Storage()
    async with s:
        event: Event = await s.event.get(event_id)
        menu: List[MenuItem] = await s.menu_item.get_items(event.menu_id)

    return {
        "event": event,
        "menu": menu
    }


class ProlongRequest(BaseModel):
    time: int


@control_router.post("/{event_id}/prolong")
async def prolong(
        event_id:int,
        prolong: ProlongRequest,
        app: Application = Depends(get_bot),
        shaas_token: Optional[str] = Cookie(default=None, alias="token")
):
    token: Token = await is_token_valid(shaas_token)

    s = Storage()
    async with s:
        event: Event = await s.event.get(event_id)

        assert event.owner_id == token.user_id

        if event.state == EventState.collecting_orders:
            event.order_end_time += datetime.timedelta(minutes=prolong.time)

            await app.bot.send_message(chat_id=event.chat_id, text=f"Событие продлено до {event.order_end_time}")

    return {
        "event": event
    }




class ReorderRequest(BaseModel):
    time: int
    entries: Dict[int, bool]


@control_router.post("/{event_id}/reorder")
async def reorder(
        event_id: int,
        reorder: ReorderRequest,
        request: Request,
        app: Application = Depends(get_bot),
        shaas_token: Optional[str] = Cookie(default=None, alias="token")
):
    token: Token = await is_token_valid(shaas_token)

    s = Storage()
    async with s:
        event: Event = await s.event.get(event_id)

        assert event.owner_id == token.user_id

        users = []
        missing_item = []
        for item_id, value in reorder.entries.items():
            if value:
                continue

            item: MenuItem = await s.menu_item.get(item_id)
            item.leftover = 0
            missing_item.append(f"- {item.name}")

            ids = await s.order.get_order_by_choice(event_id, item.id)

            for user_id in ids:
                member = await app.bot.get_chat_member(chat_id=event.chat_id, user_id=user_id)
                users.append(mention_markdown(user_id, member.user.full_name))

        await app.bot.delete_message(chat_id=event.chat_id, message_id=event.collect_message_id)

        event.state = EventState.collecting_orders
        event.order_end_time = datetime.datetime.now() + datetime.timedelta(minutes=reorder.time)
        event.collect_message_id = None

        missing_item_str = "\n".join(missing_item)
        users_str = ", ".join(users)
        text = (
            f"ТРЕБУЕТСЯ ДЕЙСТВИЕ\n"
            f"\n"
            f"Внимание! Следующих позиций нет:\n"
            f"{missing_item_str}\n"
            f"\n"
            f"Пользователи {users_str} должны перезаказать или останутся без еды!\n"
            f"Заказы открыты до {event.order_end_time.hour:02}:{event.order_end_time.minute:02}"
        )
        login = LoginUrl(f"{request.app.settings.bot.base_url}login?event_id={event.id}")
        keyboard = [
            [
                InlineKeyboardButton("Заказать", login_url=login)
            ],
        ]
        markup = InlineKeyboardMarkup(keyboard)
        order_message = await app.bot.send_message(chat_id=event.chat_id, text=text, parse_mode="markdown", reply_markup=markup)
        await order_message.pin(disable_notification=True)

        event.order_message_id = order_message.message_id

    return {

    }