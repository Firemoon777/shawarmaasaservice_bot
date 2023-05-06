from sqlalchemy import Column, Integer, BigInteger, UniqueConstraint

from shaas_web.model.base.orm import BaseTable


class Coupon(BaseTable):
    __tablename__ = "shaas_coupon"

    owner_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    count = Column(Integer, default=0, server_default="0")

    __table_args__ = (
        UniqueConstraint("owner_id", "user_id", name="_owner_user"),
    )