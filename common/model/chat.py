from sqlalchemy import Column, Integer, BigInteger

from common.model.base import BaseTable


class Chat(BaseTable):
    __tablename__ = "shaas_chat"

    chat_id = Column(BigInteger, nullable=False)