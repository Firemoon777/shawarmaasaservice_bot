from typing import List

from sqlalchemy import delete, select, func, update, desc

from shaas_common.model.menu_item.orm import MenuItem
from shaas_common.model.base import BaseRepository
from shaas_common.model.order.orm import Order, OrderEntry


class OrderRepository(BaseRepository):
    model = Order

    async def cancel_order(self, user_id, event_id):
        q = delete(self.model).where(self.model.user_id == user_id, self.model.event_id == event_id)
        await self._session.execute(q)

    async def create_order(self, user_id, event_id, order_data: dict, comment=None):
        await self.cancel_order(user_id, event_id)

        if len(order_data) == 0:
            return

        if not comment:
            comment = None

        order: Order = await self.create(
            user_id=user_id,
            event_id=event_id,
            is_taken=False,
            comment=comment
        )

        for item, count in order_data.items():
            entry = OrderEntry()
            entry.option_id = item.id
            entry.count = count
            entry.price = item.price

            order.entries.append(entry)

    async def get_order_list(self, event_id, user_id=None):
        q = select([MenuItem, func.sum(OrderEntry.count)])\
            .join(Order)\
            .join(MenuItem)\
            .where(Order.event_id == event_id)
        if user_id:
            q = q.where(Order.user_id == user_id)
        q = q.group_by(MenuItem)
        result = await self._session.execute(q)
        return list(result.fetchall())

    async def get_order_total(self, event_id):
        q = select([func.sum(OrderEntry.count)])\
            .join(Order)\
            .where(Order.event_id == event_id)
        return await self._first(q) or 0

    async def get_order_comments(self, event_id):
        q = select(self.model).where(self.model.event_id == event_id, self.model.comment != None)
        return await self._as_list(q)

    async def take_order(self, event_id, user_id):
        q = update(self.model)\
            .where(self.model.event_id == event_id, self.model.user_id == user_id)\
            .values(is_taken=True)
        await self._session.execute(q)

    async def get_pending(self, event_id) -> List:
        q = select([MenuItem.name, Order.user_id, func.sum(OrderEntry.count)])\
            .join(Order).join(MenuItem)\
            .where(Order.event_id == event_id, Order.is_taken == False)\
            .group_by(MenuItem.name, Order.user_id)

        result = await self._session.execute(q)
        return list(result.fetchall())

    async def get_comment(self, event_id, user_id) -> str:
        q = select([Order.comment]).where(Order.event_id == event_id, Order.user_id == user_id)
        return await self._first(q)

    async def get_previous_order(self, user_id) -> Order:
        q = select(self.model).where(self.model.user_id == user_id).order_by(desc(self.model.event_id))
        return await self._first(q)