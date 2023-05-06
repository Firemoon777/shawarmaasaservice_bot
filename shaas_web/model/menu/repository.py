from sqlalchemy import select

from shaas_web.model.base.repository import BaseRepository
from shaas_web.model.menu.orm import Menu


class MenuRepository(BaseRepository):
    model = Menu

    async def get_menu(self, chat_id):
        q = select(self.model).where(self.model.chat_id == chat_id)
        result = await self._session.execute(q)
        return list(result.scalars())
