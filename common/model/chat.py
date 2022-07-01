from sqlalchemy import Column, Integer, BigInteger
from sqlalchemy.orm import relationship

from common.model.base import BaseTable


class Chat(BaseTable):
    __tablename__ = "shaas_chat"

    chat_id = Column(BigInteger, nullable=False)
    menu = relationship("Menu")