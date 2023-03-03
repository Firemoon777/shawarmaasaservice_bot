import json
import logging
from typing import Optional, List, Dict

import telegram.error
from fastapi import APIRouter, Depends, Cookie
from pydantic import BaseModel
from sqlalchemy import select
from starlette.background import BackgroundTasks
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from telegram.ext import Application
from telegram.helpers import escape_markdown

from shaas_common.billing import calc_price, get_html_price_message
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

    msg = "Заказ принят!\n\n" + get_html_price_message(order_data, order.comment)

    try:
        await app.bot.send_message(chat_id=token.user_id, text=msg, parse_mode="html")
    except Exception as e:
        logging.warning(f"Unable to send message to {token.user_id}, reason: {e}")
        return {"status": "ok", "error": "bot"}

    return {"status": "ok"}