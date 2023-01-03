from typing import List

from sqlalchemy import select

from shaas_common.model.menu_item.orm import MenuItem
from shaas_common.model.base import BaseRepository


class MenuItemRepository(BaseRepository):
    model = MenuItem

    async def get_items(self, menu_id) -> List[MenuItem]:
        q = select(self.model).where(self.model.menu_id == menu_id).order_by(self.model.id)
        return await self._as_list(q)