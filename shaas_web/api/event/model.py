from datetime import datetime
from typing import Optional

from pydantic import validator

from shaas_web.api.base import BaseResponseModel
from shaas_web.model import EventState


class EventResponse(BaseResponseModel):
    state: EventState
    owner_id: Optional[int] = None
    admin_message_id: Optional[int] = None

    chat_id: int
    order_message_id: Optional[int] = None
    additional_message_id: Optional[int] = None
    collect_message_id: Optional[int] = None

    menu_id: int

    available_slots: int
    delivery_info: Optional[str] = None
    order_end_time: datetime
    money_message: Optional[str] = None


class CreateEventRequest(BaseResponseModel):
    chat_id: int
    end_time: datetime
    menu_id: int

    available_slots: int = 0
    order_time_data: str = ""
    money_msg: Optional[str] = None

    @validator('end_time')
    def end_time_in_future(cls, v):
        v = v.replace(tzinfo=None)
        if v < datetime.now():
            raise ValueError("must be in future")
        return v