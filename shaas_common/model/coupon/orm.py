import enum
from typing import Optional

from sqlalchemy import Column, Integer, BigInteger, ForeignKey, String, DateTime, Enum, desc, select, JSON, \
    UniqueConstraint
from sqlalchemy.orm import relationship

from shaas_common.model.base.orm import BaseTable


class Coupon(BaseTable):
    __tablename__ = "shaas_coupon"

    owner_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    count = Column(Integer, default=0, server_default="0")

    __table_args__ = (
        UniqueConstraint("owner_id", "user_id", name="_owner_user"),
    )