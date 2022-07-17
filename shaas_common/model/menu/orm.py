from typing import List, Optional

from sqlalchemy import Column, Integer, String, ForeignKey, select, BigInteger, cast
from sqlalchemy.orm import relationship

from shaas_common.model.base import BaseTable


class Menu(BaseTable):
    __tablename__ = "shaas_menu"

    name = Column(String, nullable=False)

    chat_id = Column(BigInteger, nullable=False)
    items = relationship("MenuItem")
