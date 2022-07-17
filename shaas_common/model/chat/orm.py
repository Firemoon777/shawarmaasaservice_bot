import enum
from typing import Optional

from sqlalchemy import Column, Integer, BigInteger, ForeignKey, String, DateTime, Enum, desc, select, JSON
from sqlalchemy.orm import relationship

from shaas_common.model.base.orm import BaseTable


class Chat(BaseTable):
    __tablename__ = "shaas_chat"

    chat_id = Column(BigInteger, unique=True, nullable=False)

