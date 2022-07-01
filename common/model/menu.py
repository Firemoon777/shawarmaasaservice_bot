from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from common.model.base import BaseTable


class Menu(BaseTable):
    __tablename__ = "shaas_menu"

    name = Column(String, nullable=False)

    items = relationship("MenuItem")