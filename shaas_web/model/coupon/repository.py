from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from shaas_web.model.base.repository import BaseRepository
from shaas_web.model.coupon.orm import Coupon


class CouponRepository(BaseRepository):
    model = Coupon

    async def get_coupons(self, owner_id: int, user_id: int) -> int:
        q = select(self.model.count).where(self.model.owner_id == owner_id, self.model.user_id == user_id, self.model.count > 0)
        return await self._first(q) or 0

    async def update_coupon_count(self, owner_id: int, user_id: int, count: int) -> None:
        q = insert(self.model).values(owner_id=owner_id, user_id=user_id, count=count).on_conflict_do_update(
            constraint="_owner_user",
            set_=dict(count=count)
        )
        await self._session.execute(q)

    async def increase_coupon_count(self, owner_id: int, user_id: int, count: int) -> None:
        q = insert(self.model).values(owner_id=owner_id, user_id=user_id, count=count).on_conflict_do_update(
            constraint="_owner_user",
            set_=dict(count=self.model.count + count)
        )
        await self._session.execute(q)