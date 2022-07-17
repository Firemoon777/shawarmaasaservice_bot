from lazy import lazy
from sqlalchemy.ext.asyncio import AsyncSession

from shaas_common.model.chat.repository import ChatRepository
from shaas_common.model.event.repository import EventRepository
from shaas_common.model.menu.repository import MenuRepository
from shaas_common.model.menu_item.repository import MenuItemRepository
from shaas_common.model.order.repository import OrderRepository
from shaas_common.session import SessionLocal


class Storage:
    def __init__(self):
        self._session: AsyncSession = SessionLocal()

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()

    @lazy
    def chat(self) -> ChatRepository:
        return ChatRepository(self._session)

    @lazy
    def event(self) -> EventRepository:
        return EventRepository(self._session)

    @lazy
    def menu(self) -> MenuRepository:
        return MenuRepository(self._session)

    @lazy
    def menu_item(self) -> MenuItemRepository:
        return MenuItemRepository(self._session)

    @lazy
    def order(self) -> OrderRepository:
        return OrderRepository(self._session)


async def get_db() -> Storage:
    db = Storage()
    yield db

    await db.commit()