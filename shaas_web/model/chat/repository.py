from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from shaas_web.model.base.repository import BaseRepository
from shaas_web.model.chat.orm import Chat


class ChatRepository(BaseRepository):
    model = Chat

    async def update_chat(self, chat_id, name, username=None):
        q = insert(self.model).values(id=chat_id, name=name, username=username).on_conflict_do_update(
            index_elements=["id"],
            set_=dict(name=name, username=username)
        )
        await self._session.execute(q)

    async def get_by_username(self, username) -> Chat:
        q = select(self.model).where(self.model.username == username)
        return await self._first(q)
