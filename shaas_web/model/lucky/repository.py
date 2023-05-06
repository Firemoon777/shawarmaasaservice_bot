from sqlalchemy import select, desc
from sqlalchemy.dialects.postgresql import insert

from shaas_web.model.base.repository import BaseRepository
from shaas_web.model.lucky.orm import LuckyAttempt


class LuckyAttemptRepository(BaseRepository):
    model = LuckyAttempt

    async def get_last_attempt(self, user_id: int) -> LuckyAttempt:
        q = select(self.model)\
            .where(self.model.user_id == user_id)\
            .order_by(desc(self.model.id))
        return await self._first(q)
