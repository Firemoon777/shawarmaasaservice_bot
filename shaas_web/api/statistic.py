import datetime
import hmac
import hashlib
import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends, Cookie, Form, File, UploadFile, HTTPException
from pydantic import BaseModel
from shaas_common.action.admin import get_controlled_chats
from starlette.requests import Request
from starlette.responses import Response
from telegram.ext import Application

from shaas_common.exception.api import ForbiddenError
from shaas_common.model import Token, Event
from shaas_common.security import is_token_valid
from shaas_common.storage import Storage
from shaas_web.bot import get_bot

statistic_router = APIRouter(prefix="/stat")


class StatModel(BaseModel):
    chat_id: int


@statistic_router.get("/")
async def check(
        chat_id: int,
        shaas_token: Optional[str] = Cookie(default=None, alias="token"),
        app: Application = Depends(get_bot),
):
    token: Token = await is_token_valid(shaas_token)
    admin_chats = await get_controlled_chats(app.bot, token.user_id)

    chat_info = None
    for chat in admin_chats:
        if chat.id == chat_id:
            chat_info = chat
            break
    else:
        raise ForbiddenError()

    s = Storage()
    async with s:
        result = await s.order.get_all_orders_for_chat(chat_id)
        return {
            "chat": chat_info,
            "stat": result
        }