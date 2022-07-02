from typing import List, Optional

from sqlalchemy import Column, Integer, String, ForeignKey, select, BigInteger, cast
from sqlalchemy.orm import relationship

from shaas_common.model.base import BaseTable


class Menu(BaseTable):
    __tablename__ = "shaas_menu"

    name = Column(String, nullable=False)

    chat_id = Column(BigInteger, nullable=False)
    items = relationship("MenuItem")

    @staticmethod
    async def get(db, menu_id) -> Optional["Menu"]:
        q = select(Menu).where(Menu.id == menu_id)
        result = await db.execute(q)
        result_list = list(result.scalars())
        if len(result_list) == 1:
            return result_list[0]
        return None

    @staticmethod
    async def chat_menu(db, chat_id) -> List["Menu"]:
        q = select(Menu).where(Menu.chat_id == chat_id)
        result = await db.execute(q)
        return list(result.scalars())
