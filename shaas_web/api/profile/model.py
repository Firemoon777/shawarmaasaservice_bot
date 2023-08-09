import datetime
from typing import List

from shaas_web.api.base import ClearBaseModel
from shaas_web.api.event.model import OrderResponse


class MyPendingOrderModel(ClearBaseModel):
    chat_name: str
    order_id: int
    event_id: int
    event_date: datetime.date
    data: OrderResponse = OrderResponse()
    is_taken: bool = False


class MyPendingOrderResponse(ClearBaseModel):
    orders: List[MyPendingOrderModel] = list()