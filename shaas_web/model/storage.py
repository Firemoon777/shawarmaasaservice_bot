from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from shaas_web.model.lucky import LuckyAttemptRepository
from shaas_web.model.token.repository import TokenRepository
from shaas_web.model.coupon.repository import CouponRepository
from shaas_web.model.chat.repository import ChatRepository
from shaas_web.model.event.repository import EventRepository
from shaas_web.model.menu.repository import MenuRepository
from shaas_web.model.menu_item.repository import MenuItemRepository
from shaas_web.model.order.repository import OrderRepository
from shaas_web.session import SessionLocal


class Storage:

    _session: Optional[AsyncSession] = None
    _lazy_attr: dict

    def __init__(self):
        self._lazy_attr = dict()

    async def __aenter__(self):
        assert self._session is None, f"re-enter is forbidden!"
        self._lazy_attr.clear()
        self._session: AsyncSession = SessionLocal()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if not self._session:
            return

        if exc_type:
            await self.rollback()
        else:
            await self.commit()

        await self._session.close()
        self._session = None

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()

    def _lazy(self, cls):
        if cls.__name__ not in self._lazy_attr:
            self._lazy_attr[cls.__name__] = cls(self._session)

        return self._lazy_attr[cls.__name__]

    @property
    def chat(self) -> ChatRepository:
        return self._lazy(ChatRepository)

    @property
    def event(self) -> EventRepository:
        return self._lazy(EventRepository)

    @property
    def menu(self) -> MenuRepository:
        return self._lazy(MenuRepository)

    @property
    def menu_item(self) -> MenuItemRepository:
        return self._lazy(MenuItemRepository)

    @property
    def order(self) -> OrderRepository:
        return self._lazy(OrderRepository)

    @property
    def token(self) -> TokenRepository:
        return self._lazy(TokenRepository)

    @property
    def coupon(self) -> CouponRepository:
        return self._lazy(CouponRepository)

    @property
    def lucky(self) -> LuckyAttemptRepository:
        return self._lazy(LuckyAttemptRepository)


async def get_db() -> Storage:
    db = Storage()
    yield db
