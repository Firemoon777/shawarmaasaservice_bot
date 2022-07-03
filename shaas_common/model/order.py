import enum
from typing import Optional, List

from sqlalchemy import Column, Integer, BigInteger, ForeignKey, String, DateTime, Enum, desc, select, delete, Boolean, \
    func
from sqlalchemy.orm import relationship

from shaas_common.model.base import BaseTable


class Order(BaseTable):
    __tablename__ = "shaas_order"

    user_id = Column(BigInteger, nullable=False)
    event_id = Column(Integer, ForeignKey("shaas_event.id"), nullable=False)

    option = Column(Integer, ForeignKey("shaas_menu_item.id"), nullable=False)
    count = Column(Integer, nullable=False)

    is_taken = Column(Boolean, default=False)

    @staticmethod
    async def submit_order(db, user_id, event_id, data: dict):
        q = delete(Order).where(Order.user_id == user_id, Order.event_id == event_id)
        await db.execute(q)

        for k, v in data.items():
            order = Order()
            order.user_id = user_id
            order.event_id = event_id
            order.option = k
            order.count = v

            db.add(order)

        await db.commit()

    @staticmethod
    async def get_sum(db, event_id) -> int:
        q = select(func.sum(Order.count)).where(Order.event_id == event_id)
        result = await db.execute(q)
        result_list = list(result.scalars())
        return result_list[0] if result_list[0] else 0


    @staticmethod
    async def get_all(db, event_id) -> List["Order"]:
        q = select(Order.count).where(Order.event_id == event_id)
        result = await db.execute(q)
        result_list = list(result.scalars())
        return result_list
