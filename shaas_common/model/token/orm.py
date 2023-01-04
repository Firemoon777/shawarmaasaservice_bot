import enum
from typing import Optional

from sqlalchemy import Column, Integer, BigInteger, ForeignKey, String, DateTime, Enum, desc, select, JSON
from sqlalchemy.orm import relationship

from shaas_common.model.base.orm import BaseTable


class Token(BaseTable):
    __tablename__ = "shaas_token"

    user_id = Column(BigInteger, ForeignKey("shaas_chat.id"), nullable=False)
    token = Column(String, nullable=False)

    expires_in = Column(DateTime, nullable=False)

