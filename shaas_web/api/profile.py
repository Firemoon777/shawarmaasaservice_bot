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

from shaas_common.model import Token, Event
from shaas_common.security import is_token_valid
from shaas_common.storage import Storage
from shaas_web.bot import get_bot

profile_router = APIRouter(prefix="/profile")


@profile_router.get("/own_events")
async def check(shaas_token: Optional[str] = Cookie(default=None, alias="token")):
    token: Token = await is_token_valid(shaas_token)

    s = Storage()
    async with s:
        events: List[Event] = await s.event.get_active_for_owner(token.user_id)

    return events


@profile_router.get("/chats")
async def check(
        shaas_token: Optional[str] = Cookie(default=None, alias="token"),
        app: Application = Depends(get_bot)
    ):
    token: Token = await is_token_valid(shaas_token)

    result = await get_controlled_chats(app.bot, token.user_id)

    return result