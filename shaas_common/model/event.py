import enum
from typing import Optional

from sqlalchemy import Column, Integer, BigInteger, ForeignKey, String, DateTime, Enum, desc, select, JSON
from sqlalchemy.orm import relationship

from shaas_common.model.base import BaseTable


class EventState(enum.Enum):
    collecting_orders = 1
    delivery = 2
    finished = 3


class Event(BaseTable):
    __tablename__ = "shaas_event"

    state = Column(Enum(EventState), default=EventState.collecting_orders)

    chat_id = Column(BigInteger, nullable=False)
    poll_message_id = Column(BigInteger, nullable=False)
    poll_id = Column(String, nullable=False)
    collect_message_id = Column(BigInteger, nullable=True)
    skip_option = Column(Integer, nullable=False)
    poll_options = Column(JSON, nullable=True)  # TODO: nope, not null

    menu_id = Column(Integer, ForeignKey("shaas_menu.id"))
    menu = relationship("Menu", lazy='joined')

    available_slots = Column(Integer, default=0, server_default="0")
    delivery_info = Column(String, default="", server_default="")
    order_end_time = Column(DateTime, nullable=False)

    @staticmethod
    async def is_active(db, chat_id) -> Optional["Event"]:
        q = select(Event).where(Event.chat_id == chat_id, Event.state != EventState.finished)
        result = await db.execute(q)
        result_list = list(result.scalars())
        if len(result_list) == 0:
            return None
        return result_list[0]

    @staticmethod
    async def is_open(db, chat_id):
        q = select(Event).where(Event.chat_id == chat_id, Event.state == EventState.collecting_orders)
        result = await db.execute(q)
        result_list = list(result.scalars())
        if len(result_list) == 0:
            return None
        return result_list[0]

    @staticmethod
    async def get_previous(db, chat_id) -> Optional["Event"]:
        q = select(Event).where(Event.chat_id == chat_id, Event.state == EventState.finished).order_by(desc(Event.id))
        result = await db.execute(q)
        result_list = list(result.scalars())
        if len(result_list) > 0:
            return result_list[0]
        return None

    @staticmethod
    async def get_by_poll(db, poll_id) -> Optional["Event"]:
        q = select(Event).where(Event.poll_id == poll_id)
        result = await db.execute(q)
        result_list = list(result.scalars())
        if len(result_list) > 0:
            return result_list[0]
        return None

    @staticmethod
    async def get(db, event_id) -> Optional["Event"]:
        q = select(Event).where(Event.id == event_id)
        result = await db.execute(q)
        result_list = list(result.scalars())
        if len(result_list) > 0:
            return result_list[0]
        return None

