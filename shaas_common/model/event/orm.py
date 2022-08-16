import enum
from typing import Optional

from sqlalchemy import Column, Integer, BigInteger, ForeignKey, String, DateTime, Enum, desc, select, JSON
from sqlalchemy.orm import relationship

from shaas_common.model.base.orm import BaseTable


class EventState(enum.Enum):
    collecting_orders = 1
    delivery = 2
    finished = 3


class Event(BaseTable):
    __tablename__ = "shaas_event"

    state = Column(Enum(EventState), default=EventState.collecting_orders)

    chat_id = Column(BigInteger, nullable=False)
    order_message_id = Column(BigInteger, nullable=True)
    additional_message_id = Column(BigInteger, nullable=True)
    collect_message_id = Column(BigInteger, nullable=True)

    menu_id = Column(Integer, ForeignKey("shaas_menu.id"))
    menu = relationship("Menu", lazy='joined')

    available_slots = Column(Integer, default=0, server_default="0")
    delivery_info = Column(String, default="", server_default="")
    order_end_time = Column(DateTime, nullable=False)
    money_message = Column(String, nullable=True)

    # DEPRECATED
    poll_message_id = Column(BigInteger, nullable=True)
    poll_id = Column(String, nullable=True)
    skip_option = Column(Integer, nullable=True)
    poll_options = Column(JSON, nullable=True)  # TODO: nope, not null