from typing import Optional

from fastapi import APIRouter, Depends, Cookie, Form, File, UploadFile
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse
from starlette.templating import Jinja2Templates
from telegram.error import BadRequest
from telegram.ext import Application

from shaas_common.exception.api import ForbiddenError
from shaas_common.model import MenuItem
from shaas_common.security import is_valid
from shaas_common.storage import Storage, get_db
from shaas_web.bot import get_bot

admin_router = APIRouter(prefix="/admin")

templates = Jinja2Templates(directory="templates")


@admin_router.get("/")
async def admin_chat_list(
    request: Request,
    user_id: int = Cookie(),
    db: Storage = Depends(get_db),
    app: Application = Depends(get_bot)
):
    chats = await db.chat.all()
    available = []
    for chat in chats:
        try:
            admins = await app.bot.get_chat_administrators(chat.chat_id)
            for admin in admins:
                if admin.user.id == user_id:
                    tg_chat = await app.bot.get_chat(chat.chat_id)
                    available.append({
                        "link": f"chat{chat.id}",
                        "name": tg_chat.title
                    })
        except BadRequest:
            continue

    data = {
        "request": request,
        "header": "Доступные чаты",
        "entry_list": available
    }
    return templates.TemplateResponse("list.html", data)


@admin_router.get("/chat{chat_id}")
async def admin_menu_list(
    request: Request,
    chat_id: int,
    user_id: int = Cookie(),
    db: Storage = Depends(get_db),
    app: Application = Depends(get_bot)
):
    chat = await db.chat.get(chat_id)
    if not chat:
        raise ForbiddenError()
    try:
        member = await app.bot.getChatMember(chat.chat_id, user_id)
        if member.status not in [member.ADMINISTRATOR, member.OWNER]:
            raise ForbiddenError()
    except BadRequest:
        raise ForbiddenError()

    menu_list = await db.menu.get_menu(chat.chat_id)

    available = []
    for menu in menu_list:
        available.append({
            "link": f"menu{menu.id}",
            "name": menu.name
        })

    data = {
        "request": request,
        "header": "Доступные меню чата",
        "entry_list": available
    }
    return templates.TemplateResponse("list.html", data)


@admin_router.get("/menu{menu_id}")
async def admin_menu_show(
    request: Request,
    menu_id: int,
    user_id: int = Cookie(),
    db: Storage = Depends(get_db),
    app: Application = Depends(get_bot)
):
    menu = await db.menu.get(menu_id)
    if not menu:
        raise ForbiddenError()
    try:
        member = await app.bot.getChatMember(menu.chat_id, user_id)
        if member.status not in [member.ADMINISTRATOR, member.OWNER]:
            raise ForbiddenError()
    except BadRequest:
        raise ForbiddenError()

    menu_list = await db.menu_item.get_items(menu_id)

    data = {
        "request": request,
        "menu": menu,
        "menu_list": menu_list
    }
    return templates.TemplateResponse("edit.html", data)


@admin_router.post("/item{item_id}")
async def admin_menu_show(
    request: Request,
    item_id: int,
    user_id: int = Cookie(),
    file: UploadFile = File(), name = Form(),
    db: Storage = Depends(get_db),
    app: Application = Depends(get_bot)
):
    item: Optional[MenuItem] = await db.menu_item.get(item_id)
    if not item:
        raise ForbiddenError()
    menu = await db.menu.get(item.menu_id)
    try:
        member = await app.bot.getChatMember(menu.chat_id, user_id)
        if member.status not in [member.ADMINISTRATOR, member.OWNER]:
            raise ForbiddenError()
    except BadRequest:
        raise ForbiddenError()

    ext = file.filename.split(".")[-1]
    item.picture = f"static/item{item_id}.{ext}"
    with open(item.picture, "wb+") as f:
        f.write(await file.read())

    await db.commit()

    return RedirectResponse(url=f"menu{item.menu_id}", status_code=301)