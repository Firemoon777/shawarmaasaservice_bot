import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, Cookie
from telegram._bot import BT

from shaas_web.api.event.model import EventListResponse, EventResponse
from shaas_web.api.event.router import show_my_order
from starlette.requests import Request


from shaas_web.api.profile.model import MyPendingOrderModel, MyPendingOrderResponse
from shaas_web.model import Token, Event
from shaas_common.security import is_token_valid
from shaas_web.model.storage import Storage
from shaas_web.bot import get_bot
from shaas_web.security import get_controlled_chats

profile_router = APIRouter(prefix="/profile", tags=["Profile"])


@profile_router.get("/order/pending", response_model=MyPendingOrderResponse)
async def get_order_history(request: Request):
    s = Storage()

    result = MyPendingOrderResponse()
    async with s:
        data = await s.order.get_user_orders(request.state.user_id)
        for chat, event, order in data:
            entry = MyPendingOrderModel(
                chat_name=chat.name,
                event_id=event.id,
                order_id=order.id,
                event_date=event.order_end_time.date(),
                data=await show_my_order(event.id, request),
                is_taken=order.is_taken
            )

            result.orders.append(entry)

    return result


@profile_router.get("/order/history")
async def get_order_history(request: Request):
    pass


@profile_router.get("/events", response_model=EventListResponse)
async def check(request: Request, bot: BT = Depends(get_bot)):
    s = Storage()
    async with s:
        chats = await get_controlled_chats(bot, request.state.user_id)
        chat_dict = {chat.id: chat.name for chat in chats}
        events: List[Event] = await s.event.get_events_for_chats(list(chat_dict.keys()))

    return EventListResponse(
        events=[
            EventResponse(
                chat_name=chat_dict[event.chat_id],
                **event.__dict__
            ) for event in events
        ]
    )
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