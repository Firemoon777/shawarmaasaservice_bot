from typing import List

from sqlalchemy import select, update

from shaas_web.model.menu_item.orm import MenuItem
from shaas_web.model.base import BaseRepository


class MenuItemRepository(BaseRepository):
    model = MenuItem

    async def get_items(self, menu_id) -> List[MenuItem]:
        q = select(self.model).where(self.model.menu_id == menu_id).order_by(self.model.id)
        return await self._as_list(q)

    async def renew_leftovers(self, menu_id):
        q = update(self.model).where(self.model.menu_id == menu_id).values(leftover=100)
        await self._session.execute(q)