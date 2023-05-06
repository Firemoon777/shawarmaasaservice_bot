from fastapi import APIRouter, Depends
from starlette.requests import Request
from telegram._bot import BT

from shaas_web.api.event.model import EventResponse
from shaas_web.bot import get_bot
from shaas_web.exceptions import AlreadyRunningError
from shaas_web.model.storage import Storage
from shaas_web.security import is_admin_in_chat

chat_router = APIRouter(prefix="/chat", tags=["Chat"])


@chat_router.get("/{chat_id}/last_event", response_model=EventResponse)
async def get_last_event(chat_id: int, request: Request, bot: BT = Depends(get_bot)):
    await is_admin_in_chat(bot, chat_id, request.state.user_id, raises=True)

    s = Storage()

    async with s:
        event = await s.event.get_last_event(chat_id)

    return EventResponse(**event.__dict__)
