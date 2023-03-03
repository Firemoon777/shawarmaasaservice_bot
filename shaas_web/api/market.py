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
from shaas_common.model import Menu, MenuItem, Event, Order, EventState, Token, Coupon
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
        if not event:
            raise ForbiddenError()

        menu: List[MenuItem] = await s.menu_item.get_items(event.menu_id)

        coupons_count: int = await s.coupon.get_coupons(event.owner_id, token.user_id)
        if coupons_count:
            coupon: MenuItem = await s.menu_item.get(0)

    if coupons_count:
        # outside ORM transaction
        coupon.leftover = coupons_count
        menu.insert(0, coupon)

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
    token: Token = await is_token_valid(shaas_token)

    s = Storage()
    order_data = dict()
    used_coupons = order.order[0] if 0 in order.order else 0
    async with s:
        event: Event = await s.event.get(order.event_id)
        if not event:
            raise ForbiddenError()

        if event.state != EventState.collecting_orders:
            raise ForbiddenError()

        for key_id, value in order.order.items():
            key = await s.menu_item.get(key_id)
            order_data[key] = value

        coupons_count: int = await s.coupon.get_coupons(event.owner_id, token.user_id)
        assert used_coupons <= coupons_count
        await s.coupon.update_coupon_count(event.owner_id, token.user_id, coupons_count - used_coupons)

        await s.order.create_order(token.user_id, event.id, order_data, order.comment)

    total = 0

    paid_items_list = []
    free_items_list = []
    for item, count in order_data.items():
        if item.id == 0:
            continue

        paid_items_list.extend([item] * count)

    paid_items_list.sort(key=lambda x: x.price, reverse=True)

    for i in range(used_coupons):
        free_items_list.append(paid_items_list.pop(0))

    paid_items_dict = dict()
    for item in paid_items_list:
        if item not in paid_items_dict:
            paid_items_dict[item] = 0
        paid_items_dict[item] += 1

    free_items_dict = dict()
    for item in free_items_list:
        if item not in free_items_dict:
            free_items_dict[item] = 0
        free_items_dict[item] += 1

    msg = "Заказ принят!\n\n"
    for item, count in paid_items_dict.items():
        total += count*item.price
        msg += f"{count}x {item.name} - {count*item.price} р.\n"

    for item, count in free_items_dict.items():
        msg += f"{count}x {item.name} - <s>{count * item.price} р.</s> 0 р.\n"

    msg += f"\nИтого: {total} р."

    if order.comment:
        msg += f'\n\nКомментарий:\n{order.comment.replace("<", "&lt;").replace(">", "&gt;")}'

    await app.bot.send_message(chat_id=token.user_id, text=msg, parse_mode="html")

    return {"status": "ok"}