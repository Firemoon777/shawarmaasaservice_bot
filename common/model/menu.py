from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from common.model.base import BaseTable


class Menu(BaseTable):
    __tablename__ = "shaas_menu"

    name = Column(String, nullable=False)

    chat_id = Column(Integer, ForeignKey("shaas_chat.id"))
    items = relationship("MenuItem")