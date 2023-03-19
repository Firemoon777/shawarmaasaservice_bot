import enum
from typing import Optional

from sqlalchemy import Column, Integer, BigInteger, ForeignKey, String, DateTime, Enum, desc, select, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from shaas_common.model.base.orm import BaseTableNoID


class Chat(BaseTableNoID):
    __tablename__ = "shaas_chat"

    id = Column(BigInteger, unique=True, nullable=False, primary_key=True)

    name = Column(String)
    username = Column(String)

    send_direct_messages = Column(Boolean, default=True, server_default=expression.true(), nullable=False)

