from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import select
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from telegram.ext import Application

from shaas_common.model import Menu, MenuItem, Event
from shaas_common.session import get_db
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

    active = await Event.is_active(db, chat_id)

    data = {
        "request": request,
        "menu": menu,
        "user_id": user_id,
        "user_hash": user_hash,
        "active": "true" if active else "false"
    }
    return templates.TemplateResponse("index.html", data)


@web_app_router.post("/order")
async def make_order(request: Request, settings = Depends(get_settings)):
    form = await request.form()
    print(form)
    user_id = form["user_id"]

    app = Application.builder().token(settings.bot.token).build()
    await app.bot.send_message(
        chat_id=user_id,
        text="Заказ принят!"
    )

    return {
        "ok": True
    }