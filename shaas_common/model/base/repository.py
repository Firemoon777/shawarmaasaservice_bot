from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from shaas_common.model.base.orm import BaseTable


class BaseRepository:
    model = BaseTable

    def __init__(self, session):
        self._session: AsyncSession = session

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()

    async def _first(self, query):
        result = await self._session.execute(query)
        obj = result.first()
        if obj is None:
            return None

        return obj[0]

    async def get(self, id):
        q = select(self.model).where(self.model.id == id)
        return await self._first(q)

    async def all(self):
        q = select(self.model)
        return await self._as_list(q)

    async def _as_list(self, q):
        result = await self._session.execute(q)
        return list(result.scalars())

    async def create(self, **kwargs):
        obj = self.model()
        for k, v in kwargs.items():
            setattr(obj, k, v)
        self._session.add(obj)
        return obj

    async def update(self, id, **kwargs):
        obj = await self.get(id)
        for k, v in kwargs.items():
            setattr(obj, k, v)

    async def delete(self, id):
        q = delete(self.model).where(self.model.id == id)
        await self._session.execute(q)