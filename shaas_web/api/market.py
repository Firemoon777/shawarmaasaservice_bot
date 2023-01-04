import json
from typing import Optional, List, Dict

from fastapi import APIRouter, Depends, Cookie
from pydantic import BaseModel
from sqlalchemy import select
from starlette.background import BackgroundTasks
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from telegram.ext import Application
from telegram.helpers import escape_markdown

from shaas_common.exception.api import ForbiddenError
from shaas_common.model import Menu, MenuItem, Event, Order, EventState, Token
from shaas_common.poll import close_poll_if_necessary
from shaas_common.security import is_token_valid
from shaas_common.settings import get_settings
from shaas_common.storage import Storage, get_db
from shaas_web.bot import get_bot

market_router = APIRouter(prefix="/market")


@market_router.get("/{event_id}")
async def get_event_menu(
        event_id: int,
        shaas_token: Optional[str] = Cookie(default=None, alias="token"),
        app: Application = Depends(get_bot)
):
    token: Token = await is_token_valid(shaas_token)

    s = Storage()
    async with s:
        event: Event = await s.event.get(event_id)
        menu: List[MenuItem] = await s.menu_item.get_items(event.menu_id)

    member = await app.bot.get_chat_member(chat_id=event.chat_id, user_id=token.user_id)
    if not member:
        raise ForbiddenError()

    return {
        "event": EventState(event.state).name,
        "menu": menu
    }


class OrderRequest(BaseModel):
    event_id: int
    order: Dict[int, int]
    comment: Optional[str] = ""


@market_router.post("/order")
async def place_order(
        order: OrderRequest,
        shaas_token: Optional[str] = Cookie(default=None, alias="token"),
        app: Application = Depends(get_bot)
):
    print(order)

    token: Token = await is_token_valid(shaas_token)

    s = Storage()
    order_data = dict()
    async with s:
        event: Event = await s.event.get(order.event_id)
        if event.state != EventState.collecting_orders:
            raise ForbiddenError()

        for key_id, value in order.order.items():
            # key_id = int(key_id)
            key = await s.menu_item.get(key_id)
            order_data[key] = value

        await s.order.create_order(token.user_id, event.id, order_data, order.comment)

    total = 0
    msg = "Заказ принят!\n\n"
    for item, count in order_data.items():
        total += count*item.price
        msg += f"{count}x {item.name} - {count*item.price} р.\n"
    msg += f"\nИтого: {total} р."

    if order.comment:
        msg += f"\n\nКомментарий:\n{order.comment}"

    await app.bot.send_message(chat_id=token.user_id, text=msg)

# @market_router.post("/order")
# async def make_order(request: Request, background_tasks: BackgroundTasks, app = Depends(get_bot)):
#     s = Storage()
#
#     form = await request.form()
#
#     user_id = int(form["user_id"])
#     order_raw = json.loads(form["order_data"])
#     event_id = int(form["event_id"])
#     comment = form.get("comment")
#     # comment = escape_markdown(comment)
#
#     async with s:
#         event = await s.event.get(event_id)
#
#     if event.state != EventState.collecting_orders:
#         await app.bot.send_message(
#             chat_id=user_id,
#             text="Это меню для события, которое уже закрыто.\n\nЗаказ не оформлен."
#         )
#         return {
#             "ok": True
#         }
#
#     order_data = dict()
#
#     async with s:
#         for row in order_raw:
#             key_id = int(row["id"])
#             key = await s.menu_item.get(key_id)
#             value = int(row["count"])
#             order_data[key] = value
#
#         await s.order.create_order(user_id, event.id, order_data, comment)
#
#     items_str = []
#     total_price = 0
#     for item, count in order_data.items():
#         price = count*item.price
#         total_price += price
#         items_str.append(
#             f"{count}x {item.name} - {price} р."
#         )
#
#     msg = "Заказ принят!\n\n" + "\n".join(items_str) + f"\n\nИтого: {total_price} р."
#     if comment:
#         msg += f"\n\nКомментарий:\n{comment}"
#
#     await app.bot.send_message(
#         chat_id=user_id,
#         text=msg
#     )
#
#     await close_poll_if_necessary(s, app.bot, event.id)
#     # background_tasks.add_task(close_poll_if_necessary, s, app.bot, event_id)
#
#     return {
#         "ok": True
#     }