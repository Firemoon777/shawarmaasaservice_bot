from typing import Optional, List

from fastapi import APIRouter, Depends, Cookie
from starlette.requests import Request

from shaas_common.action.admin import get_controlled_chats
from telegram.ext import Application

from shaas_web.model import Token, Event
from shaas_common.security import is_token_valid
from shaas_web.model.storage import Storage
from shaas_web.bot import get_bot

profile_router = APIRouter(prefix="/profile", tags=["Profile"])


@profile_router.get("/order/history")
async def get_order_history(request: Request):
    pass


# @profile_router.get("/own_events")
# async def check(shaas_token: Optional[str] = Cookie(default=None, alias="token")):
#     token: Token = await is_token_valid(shaas_token)
#
#     s = Storage()
#     async with s:
#         events: List[Event] = await s.event.get_active_for_owner(token.user_id)
#
#     return events
#
#
# @profile_router.get("/chats")
# async def check(
#         shaas_token: Optional[str] = Cookie(default=None, alias="token"),
#         app: Application = Depends(get_bot)
#     ):
#     token: Token = await is_token_valid(shaas_token)
#
#     result = await get_controlled_chats(app.bot, token.user_id)
#
#     return result