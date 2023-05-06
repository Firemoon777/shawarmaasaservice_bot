import enum

from sqlalchemy import Column, Integer, BigInteger, ForeignKey, String, DateTime, Enum
from sqlalchemy.orm import relationship

from shaas_web.model.base.orm import BaseTable


class EventState(enum.Enum):
    collecting_orders = 1
    delivery = 2
    finished = 3


class Event(BaseTable):
    __tablename__ = "shaas_event"

    state = Column(Enum(EventState), default=EventState.collecting_orders)
    owner_id = Column(BigInteger, nullable=True)    # TODO: Not NULL
    admin_message_id = Column(BigInteger, nullable=True)

    chat_id = Column(BigInteger, nullable=False)
    order_message_id = Column(BigInteger, nullable=True)
    additional_message_id = Column(BigInteger, nullable=True)
    collect_message_id = Column(BigInteger, nullable=True)

    menu_id = Column(Integer, ForeignKey("shaas_menu.id"))
    menu = relationship("Menu", lazy='joined')

    available_slots = Column(Integer, default=0, server_default="0")
    delivery_info = Column(String, default="", server_default="")
    order_end_time = Column(DateTime, nullable=False)
    actual_order_end_time = Column(DateTime, nullable=True)
    money_message = Column(String, nullable=True)