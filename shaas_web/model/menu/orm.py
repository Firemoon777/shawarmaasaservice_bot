from sqlalchemy import Column, String, BigInteger
from sqlalchemy.orm import relationship

from shaas_web.model.base import BaseTable


class Menu(BaseTable):
    __tablename__ = "shaas_menu"

    name = Column(String, nullable=False)

    chat_id = Column(BigInteger, nullable=False)
    items = relationship("MenuItem")
