from typing import List, Optional

from sqlalchemy import Column, Integer, String, ForeignKey, Float, BigInteger, Boolean, select
from sqlalchemy.orm import relationship

from shaas_common.model.base import BaseTable


class MenuItem(BaseTable):
    __tablename__ = "shaas_menu_item"

    menu_id = Column(BigInteger, ForeignKey("shaas_menu.id"), nullable=False)

    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)

    description = Column(String, nullable=True)
    proteins = Column(Float, nullable=True)
    fats = Column(Float, nullable=True)
    carbohydrates = Column(Float, nullable=True)
    calories = Column(Float, nullable=True)

    poll_enable = Column(Boolean, default=False)

    @staticmethod
    async def get_poll_enabled(db, menu_id) -> List["MenuItem"]:
        q = select(MenuItem).where(MenuItem.menu_id == menu_id, MenuItem.poll_enable == True)
        result = await db.execute(q)
        return list(result.scalars())

    @staticmethod
    async def get(db, item_id) -> Optional["MenuItem"]:
        q = select(MenuItem).where(MenuItem.id == item_id)
        result = await db.execute(q)
        result_list = list(result.scalars())
        return result_list[0] if len(result_list) else None