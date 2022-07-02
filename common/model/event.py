import enum

from sqlalchemy import Column, Integer, BigInteger, ForeignKey, String, DateTime, Enum
from sqlalchemy.orm import relationship

from common.model.base import BaseTable


class EventState(enum.Enum):
    collecting_orders = 1
    delivery = 2
    finished = 3


class Event(BaseTable):
    __tablename__ = "shaas_event"

    state = Column(Enum(EventState), default=EventState.collecting_orders)

    chat_id = Column(BigInteger, nullable=False)
    menu_id = Column(Integer, ForeignKey("shaas_menu.id"))
    menu = relationship("Menu")

    available_slots = Column(Integer, default=0, server_default="0")
    delivery_info = Column(String, default="", server_default="")
    order_end_time = Column(DateTime, nullable=False)