import json
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import select
from starlette.background import BackgroundTasks
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from telegram.ext import Application
from telegram.helpers import escape_markdown

from shaas_common.model import Menu, MenuItem, Event, Order, EventState
from shaas_common.poll import close_poll_if_necessary
from shaas_common.settings import get_settings
from shaas_common.storage import Storage, get_db
from shaas_web.bot import get_bot

web_app_router = APIRouter()


templates = Jinja2Templates(directory="templates")


@web_app_router.get("/{menu_id}")
async def get_menu(
        menu_id: int,
        request: Request,
        s:Storage=Depends(get_db),
        user_id: Optional[int] = None,
        user_hash: Optional[str] = None,
        chat_id: Optional[int] = None
):
    menu = await s.menu_item.get_items(menu_id)

    active = await s.event.get_current(chat_id)

    data = {
        "request": request,
        "menu": menu,
        "user_id": user_id,
        "user_hash": user_hash,
        "active": "true" if active else "false",
        "event_id": active.id if active else 0
    }
    return templates.TemplateResponse("index.html", data)


@web_app_router.post("/order")
async def make_order(request: Request, background_tasks: BackgroundTasks, app = Depends(get_bot)):
    s = Storage()

    form = await request.form()

    user_id = int(form["user_id"])
    order_raw = json.loads(form["order_data"])
    event_id = int(form["event_id"])
    comment = form.get("comment")
    # comment = escape_markdown(comment)

    event = await s.event.get(event_id)

    if event.state != EventState.collecting_orders:
        await app.bot.send_message(
            chat_id=user_id,
            text="Это меню для события, которое уже закрыто.\n\nЗаказ не оформлен."
        )
        return {
            "ok": True
        }

    order_data = dict()
    for row in order_raw:
        key_id = int(row["id"])
        key = await s.menu_item.get(key_id)
        value = int(row["count"])
        order_data[key] = value

    await s.order.create_order(user_id, event.id, order_data, comment)
    await s.commit()

    items_str = []
    total_price = 0
    for item, count in order_data.items():
        price = count*item.price
        total_price += price
        items_str.append(
            f"{count}x {item.name} - {price} р."
        )

    msg = "Заказ принят!\n\n" + "\n".join(items_str) + f"\n\nИтого: {total_price} р."
    if comment:
        msg += f"\n\nКомментарий:\n{comment}"

    await app.bot.send_message(
        chat_id=user_id,
        text=msg
    )

    await close_poll_if_necessary(s, app.bot, event.id)
    # background_tasks.add_task(close_poll_if_necessary, s, app.bot, event_id)

    return {
        "ok": True
    }