from sqlalchemy import select

from shaas_web.model.base.repository import BaseRepository
from shaas_web.model.token.orm import Token


class TokenRepository(BaseRepository):
    model = Token

    async def get_by_token(self, token: str) -> Token:
        q = select(self.model).where(self.model.token == token)
        return await self._first(q)