import enum
from typing import Optional, List

from sqlalchemy import Column, Integer, BigInteger, ForeignKey, String, DateTime, Enum, desc, select, delete, Boolean, \
    func
from sqlalchemy.orm import relationship

from shaas_common.model.base import BaseTable


class OrderComment(BaseTable):
    __tablename__ = "shaas_order_comment"

    user_id = Column(BigInteger, nullable=False)
    event_id = Column(Integer, ForeignKey("shaas_event.id"), nullable=False)

    comment = Column(String, nullable=True)

    @staticmethod
    async def get_comments(db, event_id):
        q = select(OrderComment.comment).where(OrderComment.event_id == event_id)
        result = await db.execute(q)
        return list(result.scalars())

    @staticmethod
    async def submit(db, user_id, event_id, comment):
        q = delete(OrderComment).where(OrderComment.user_id == user_id, OrderComment.event_id == event_id)
        await db.execute(q)

        if comment:
            oc = OrderComment()
            oc.event_id = event_id
            oc.user_id = user_id
            oc.comment = comment
            db.add(oc)

        await db.commit()