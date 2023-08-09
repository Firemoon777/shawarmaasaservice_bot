from datetime import datetime
from typing import Optional, List, Dict

from pydantic import validator
from telegram.helpers import mention_markdown

from shaas_web.api.base import BaseResponseModel, ClearBaseModel
from shaas_web.model import EventState


class EventResponse(BaseResponseModel):
    state: EventState
    owner_id: Optional[int] = None
    admin_message_id: Optional[int] = None

    chat_id: int
    chat_name: Optional[str] = None
    order_message_id: Optional[int] = None
    additional_message_id: Optional[int] = None
    collect_message_id: Optional[int] = None

    menu_id: int

    available_slots: int
    delivery_info: Optional[str] = None
    order_end_time: datetime
    actual_order_end_time: Optional[datetime] = None
    money_message: Optional[str] = None


class EventListResponse(ClearBaseModel):
    events: List[EventResponse] = list()


class CreateEventRequest(ClearBaseModel):
    chat_id: int
    end_time: datetime
    menu_id: int

    available_slots: int = 0
    order_time_data: str = ""
    money_msg: Optional[str] = None

    @validator('end_time')
    def end_time_in_future(cls, v):
        v = datetime.fromtimestamp(v.timestamp()).replace(tzinfo=None)
        if v < datetime.now():
            raise ValueError("must be in future")
        return v


class OrderItemResponse(ClearBaseModel):
    id: int
    name: str
    price: float
    picture: str

    count: int
    is_ordered: bool


class OrderResponse(ClearBaseModel):
    order: List[OrderItemResponse] = list()
    comment: Optional[str] = None


class OrderEntry(OrderResponse):
    user_id: int
    username: Optional[str] = None
    name: str

    is_taken: bool = False
    is_ordered: bool = False

    def user_report(self) -> str:
        mention = mention_markdown(self.user_id, self.name)
        text = f"{mention}:\n"
        for entry in self.order:
            if entry.count == 0:
                continue

            text += f"{entry.count}x {entry.name}\n"

        if self.comment:
            text += f"- {self.comment.strip()}\n"

        return text


class OrderListResponse(ClearBaseModel):
    orders: List[OrderEntry]

    def total_order(self) -> str:
        full_order = dict()
        delta = dict()

        text = ""

        for user_order in self.orders:
            for entry in user_order.order:
                if entry.name not in full_order:
                    full_order[entry.name] = 0

                full_order[entry.name] += entry.count

                if not entry.is_ordered:
                    if entry.name not in delta:
                        delta[entry.name] = 0

                    delta[entry.name] += entry.count

        if full_order != delta:
            text += f"Обновление:\n"

            for name, count in delta.items():
                text += f"{count}x {name}\n"

            text += "\n"

        text += f"Полный заказ:\n"
        full_order_list = [(name, count) for name, count in full_order.items()]
        full_order_list.sort(key=lambda x: x[1], reverse=True)
        for name, count in full_order_list:
            text += f"{count}x {name}\n"

        text += "\n"

        comments = []
        for user_order in self.orders:
            if user_order.comment:
                comments.append(user_order.user_report())

        if comments:
            text += "Комментарии:\n".join(comments)

        return text


class ReorderRequest(ClearBaseModel):
    time: datetime
    entries: Dict[int, bool] = {}

    @validator('time')
    def datetime_validator(cls, v):
        return datetime.fromtimestamp(v.timestamp()).replace(tzinfo=None)


class ProlongRequest(ClearBaseModel):
    time: datetime

    @validator('time')
    def datetime_validator(cls, v):
        return datetime.fromtimestamp(v.timestamp()).replace(tzinfo=None)

