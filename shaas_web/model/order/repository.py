import datetime
from typing import List, Tuple

from sqlalchemy import delete, select, func, update, desc, distinct
from sqlalchemy.orm import selectinload, joinedload
from telegram.helpers import escape_markdown

from shaas_web.exceptions import ForbiddenError
from shaas_web.model import Coupon, Event, Chat
from shaas_web.model.menu_item.orm import MenuItem
from shaas_web.model.base import BaseRepository
from shaas_web.model.order.orm import Order, OrderEntry


class OrderRepository(BaseRepository):
    model = Order

    async def get_unique_order(self, event_id: int, user_id: int) -> Order:
        q = select(self.model).options(joinedload(self.model.entries))\
            .where(self.model.event_id == event_id)\
            .where(self.model.user_id == user_id)
        result = await self._first(q)

        if result:
            return result

        return await self.create(
            event_id=event_id,
            user_id=user_id
        )

    async def cancel_order(self, user_id, event_id, force=False):
        q = select(Event.owner_id).where(Event.id == event_id)
        owner_id = await self._first(q)

        # Влзвращаем купоны
        order_list = await self.get_orders(event_id, user_id)
        for order, chat, item, order_entry in order_list:
            if item.id == 0 and not order_entry.is_ordered:
                q = update(Coupon).where(Coupon.user_id == user_id, Coupon.owner_id == owner_id).values(count=Coupon.count + order_entry.count)
                await self._session.execute(q)

        order = await self.get_unique_order(event_id, user_id)
        q = delete(OrderEntry).where(OrderEntry.order_id == order.id).where(OrderEntry.is_ordered != True)
        await self._session.execute(q)
        return order

    async def zero_count(self, event_id, option_id):
        q = select([OrderEntry.id])\
            .join(Order)\
            .where(Order.event_id == event_id)
        entry_ids = await self._as_list(q)
        q = update(OrderEntry)\
            .where(OrderEntry.id.in_(entry_ids))\
            .where(OrderEntry.option_id == option_id)\
            .values(count=0)
        await self._session.execute(q)

    async def set_ordered(self, event_id):
        q = select([OrderEntry.id]) \
            .join(Order) \
            .where(Order.event_id == event_id)
        entry_ids = await self._as_list(q)
        q = update(OrderEntry) \
            .where(OrderEntry.id.in_(entry_ids)) \
            .values(is_ordered=True)
        await self._session.execute(q)

    async def create_order(self, user_id, event_id, order_data: dict, comment=None):
        order = await self.cancel_order(user_id, event_id)

        if len(order_data) == 0:
            return

        if not comment:
            comment = None
        else:
            comment = escape_markdown(comment)

        order.comment = comment

        for item, count in order_data.items():
            entry = OrderEntry()
            entry.option_id = item.id
            entry.count = count
            entry.price = item.price

            order.entries.append(entry)

    async def get_order_list(self, event_id, user_id=None):
        q = select([self.model.id, MenuItem, func.sum(OrderEntry.count)])\
            .join(Order)\
            .join(MenuItem)\
            .where(Order.event_id == event_id)
        if user_id:
            q = q.where(Order.user_id == user_id)
        q = q.group_by(self.model.id, MenuItem)
        result = await self._session.execute(q)
        return list(result.fetchall())

    async def get_orders(self, event_id: int, user_id: int = None) -> List[Tuple[Order, Chat, MenuItem, OrderEntry]]:
        q = select([self.model, Chat, MenuItem, OrderEntry]) \
            .join(Order) \
            .join(Chat, Order.user_id == Chat.id) \
            .join(MenuItem) \
            .where(Order.event_id == event_id)
        if user_id:
            q = q.where(Order.user_id == user_id)
        result = await self._session.execute(q)
        return list(result.fetchall())

    async def get_user_orders(self, user_id: int) -> List[Tuple[Chat, Event, Order]]:
        q = select([Chat, Event, Order])\
            .join(Event)\
            .join(Chat, Chat.id == Event.chat_id)\
            .where(self.model.user_id == user_id)\
            .where(self.model.is_taken == False)\
            .order_by(desc(self.model.id))\
            .limit(5)
        result = await self._session.execute(q)
        return list(result.fetchall())

    async def get_order_list_extended(self, event_id, user_id=None):
        q = select([self.model, Chat, func.sum(OrderEntry.price*OrderEntry.count)])\
            .join(Order)\
            .join(Chat, Order.user_id == Chat.id)\
            .where(Order.event_id == event_id)
        if user_id:
            q = q.where(Order.user_id == user_id)
        q = q.group_by(self.model, Chat)
        result = await self._session.execute(q)
        return list(result.fetchall())

    async def get_order_total(self, event_id):
        q = select([func.sum(OrderEntry.count)])\
            .join(Order)\
            .where(Order.event_id == event_id).where(OrderEntry.option_id > 0)
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

    async def get_previous_order(
            self,
            user_id: int,
            current_event_id: int = None,
            current_chat_id: int = None
    ) -> Order:
        q = select(self.model).where(self.model.user_id == user_id)
        if current_event_id:
            q = q.where(self.model.event_id != current_event_id)
        if current_chat_id:
            q = q.join(Event).where(Event.chat_id == current_chat_id)
        q = q.order_by(desc(self.model.event_id))
        return await self._first(q)

    async def get_order_by_choice(self, event_id, menu_id) -> List[int]:
        q = select(distinct(self.model.user_id)).join(OrderEntry).where(self.model.id == OrderEntry.order_id).where(OrderEntry.option_id == menu_id).where(self.model.event_id == event_id)
        return await self._as_list(q)

    # Статистика
    async def get_all_orders_for_chat(self, chat_id, user_id=None) -> List:
        q = select([MenuItem, func.sum(OrderEntry.count).label("count"), func.sum(OrderEntry.price).label("price")]) \
            .join(Order) \
            .join(MenuItem) \
            .join(Event) \
            .where(Event.chat_id == chat_id)
        if user_id:
            q = q.where(Order.user_id == user_id)
        q = q.group_by(MenuItem)
        result = await self._session.execute(q)
        return list(result.fetchall())

    async def get_total_orders_for_user(self, chat_id, user_id=None) -> List:
        q = select([Chat, func.sum(OrderEntry.count).label("count"), func.sum(OrderEntry.price).label("price")]) \
            .join(Order) \
            .join(MenuItem) \
            .join(Event) \
            .join(Chat, Chat.id == Order.user_id) \
            .where(Event.chat_id == chat_id)
        if user_id:
            q = q.where(Order.user_id == user_id)
        q = q.group_by(Chat)
        result = await self._session.execute(q)
        return list(result.fetchall())

    async def get_current_year_statistic(self, chat_id):
        return await self.get_year_statistic(chat_id, datetime.date.today().year)

    async def get_year_statistic(self, chat_id, year: int):
        start = datetime.date(year, 1, 1)
        end = datetime.date(year, 12, 31)
        q = select([MenuItem, func.sum(OrderEntry.count)]) \
            .join(Order) \
            .join(MenuItem)\
            .join(Event)\
            .where(Event.chat_id == chat_id)\
            .where(Event.order_end_time.between(start, end))
        q = q.group_by(MenuItem)
        result = await self._session.execute(q)
        return list(result.fetchall())

    async def get_current_year_statistic_for_all_events(self, chat_id):
        return await self.get_year_statistic_for_all_events(chat_id, datetime.date.today().year)

    async def get_year_statistic_for_all_events(self, chat_id, year: int):
        start = datetime.date(year, 1, 1)
        end = datetime.date(year, 12, 31)
        q = select(Event)\
            .where(Event.chat_id == chat_id)\
            .where(Event.order_end_time.between(start, end))\
            .order_by(Event.order_end_time.asc())
        events = await self._as_list(q)

        result = dict()
        for event in events:
            q = select([MenuItem, func.sum(OrderEntry.count)]) \
                .join(Order) \
                .join(MenuItem) \
                .join(Event) \
                .where(Event.id == event.id)
            q = q.group_by(MenuItem)
            event_date = f"{event.order_end_time.year}-{event.order_end_time.month:02}-{event.order_end_time.day:02}"
            result[event_date] = list(await self._session.execute(q))
        return result
