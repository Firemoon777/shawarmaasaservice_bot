import enum
from typing import Optional

from sqlalchemy import Column, Integer, BigInteger, ForeignKey, String, DateTime, Enum, desc, select, delete
from sqlalchemy.orm import relationship

from shaas_common.model.base import BaseTable
from shaas_common.session import SessionLocal


class Order(BaseTable):
    __tablename__ = "shaas_order"

    user_id = Column(BigInteger, nullable=False)
    event_id = Column(Integer, ForeignKey("shaas_event.id"), nullable=False)

    option = Column(Integer, ForeignKey("shaas_menu_item.id"), nullable=False)
    count = Column(Integer, nullable=False)

    @staticmethod
    def submit_order(db: SessionLocal, user_id, event_id, data: dict):
        q = delete(Order).whete(Order.user_id == user_id, Order.event_id == event_id)
        await db.execute(q)

        for k, v in data.items():
            order = Order()
            order.user_id = user_id
            order.event_id = event_id
            order.option = k
            order.count = v

            db.add(order)

        await db.commit()
