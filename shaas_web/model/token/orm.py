from sqlalchemy import Column, BigInteger, ForeignKey, String, DateTime

from shaas_web.model.base.orm import BaseTable


class Token(BaseTable):
    __tablename__ = "shaas_token"

    user_id = Column(BigInteger, ForeignKey("shaas_chat.id"), nullable=False)
    token = Column(String, nullable=False)

    expires_in = Column(DateTime, nullable=False)

