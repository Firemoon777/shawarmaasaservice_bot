import random
from typing import List

from fastapi import APIRouter, Depends
from starlette.requests import Request
from telegram._bot import BT

from shaas_web.api.event.router import place_order, OrderRequest
from shaas_web.api.lucky.model import MenuItemResponse, LuckyResponse, LuckyAttemptAcceptance, LuckyAttemptRequest
from shaas_web.bot import get_bot
from shaas_web.exceptions import NotFoundError, ForbiddenError
from shaas_web.model import MenuItem, Event, EventState, LuckyAttempt
from shaas_web.model.storage import Storage

lucky_router = APIRouter(prefix="/lucky", tags=["Random"])


@lucky_router.post("/", response_model=LuckyResponse)
async def submit_lucky_attempt(data: LuckyAttemptRequest, request: Request, bot: BT = Depends(get_bot)):
    s = Storage()

    async with s:
        event: Event = await s.event.get(data.event_id)
        if not event:
            raise NotFoundError()

        if event.state != EventState.collecting_orders:
            raise ForbiddenError()

        menu_list = await s.menu_item.get_items(event.menu_id)

        menu_item: MenuItem = random.choice(menu_list)

        item = await s.lucky.create(
            user_id=request.state.user_id,
            event_id=data.event_id,
            menu_item_id=menu_item.id
        )
    return LuckyResponse(
        item=MenuItemResponse(**menu_item.__dict__),
        **item.__dict__,
    )


@lucky_router.post("/{lucky_id}")
async def accept_lucky_attempt(lucky_id: int, data: LuckyAttemptAcceptance, request: Request, bot: BT = Depends(get_bot)):
    s = Storage()

    async with s:
        lucky: LuckyAttempt = await s.lucky.get_last_attempt(request.state.user_id)

        if lucky.id != lucky_id:
            raise ForbiddenError()

        if lucky.user_id != request.state.user_id:
            raise ForbiddenError()

        event: Event = await s.event.get(lucky.event_id)
        if not event:
            raise NotFoundError()

        if event.state != EventState.collecting_orders:
            raise ForbiddenError()

        if lucky.menu_item_id != data.item_id:
            raise ForbiddenError()

        await s.lucky.update(lucky_id, accepted=True)

    order_request = OrderRequest(
        order={lucky.menu_item_id: 1},
        comment=None
    )
    return await place_order(event.id, order_request, request, bot)
