from sqlalchemy import Column, Integer, BigInteger, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from shaas_web.model.base import BaseTable


class Order(BaseTable):
    __tablename__ = "shaas_order"

    user_id = Column(BigInteger, nullable=False)
    event_id = Column(Integer, ForeignKey("shaas_event.id"), nullable=False)

    is_taken = Column(Boolean, default=False)
    is_paid = Column(Boolean, default=False, server_default=expression.false())

    comment = Column(String, nullable=True)

    entries = relationship("OrderEntry", passive_deletes="all", backref="order")


class OrderEntry(BaseTable):
    __tablename__ = "shaas_order_entry"

    order_id = Column(Integer, ForeignKey("shaas_order.id", ondelete="CASCADE"), nullable=False)

    option_id = Column(Integer, ForeignKey("shaas_menu_item.id"), nullable=False)
    count = Column(Integer, nullable=False)

    price = Column(Integer, nullable=False)

    is_ordered = Column(Boolean, default=False, server_default=expression.false())