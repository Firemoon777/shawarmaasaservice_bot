import json
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import select
from starlette.background import BackgroundTasks
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from telegram.ext import Application

from shaas_common.model import Menu, MenuItem, Event, Order, EventState, OrderComment
from shaas_common.poll import close_poll_if_necessary
from shaas_common.session import get_db, SessionLocal
from shaas_common.settings import get_settings

web_app_router = APIRouter()


templates = Jinja2Templates(directory="templates")


@web_app_router.get("/{menu_id}")
async def get_menu(
        menu_id: int,
        request: Request,
        db=Depends(get_db),
        user_id: Optional[int] = None,
        user_hash: Optional[str] = None,
        chat_id: Optional[int] = None
):
    q = select(MenuItem).where(MenuItem.menu_id == menu_id)
    result = await db.execute(q)
    menu = list(result.scalars())

    active = await Event.is_open(db, chat_id)

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
async def make_order(request: Request, background_tasks: BackgroundTasks, settings = Depends(get_settings)):
    form = await request.form()

    user_id = int(form["user_id"])
    order_raw = json.loads(form["order_data"])
    event_id = int(form["event_id"])
    comment = form.get("comment")

    session = SessionLocal()
    app = Application.builder().token(settings.bot.token).build()

    event = await Event.get(session, event_id)

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
        key = int(row["id"])
        value = int(row["count"])
        order_data[key] = value

    await OrderComment.submit(session, user_id, event_id, comment)
    await Order.submit_order(session, user_id, event_id, order_data)

    items = {
        item_id: await MenuItem.get(session, item_id) for item_id in order_data.keys()
    }
    items_str = []
    total_price = 0
    for item_id, count in order_data.items():
        item = items[item_id]
        price = count*item.price
        total_price += price
        items_str.append(
            f"{count}x {items[item_id].name} - {price} р."
        )

    await app.bot.send_message(
        chat_id=user_id,
        text="Заказ принят!\n\n" + "\n".join(items_str) + f"\n\nИтого: {total_price} р."
    )

    background_tasks.add_task(close_poll_if_necessary, session, app.bot, event.poll_id)
    # await close_poll_if_necessary(session, app.bot, event.poll_id)

    return {
        "ok": True
    }