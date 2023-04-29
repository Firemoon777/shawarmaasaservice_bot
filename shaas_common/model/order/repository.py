import datetime
from typing import List

from sqlalchemy import delete, select, func, update, desc, distinct
from telegram.helpers import escape_markdown

from shaas_common.model import Coupon, Event, Chat
from shaas_common.model.menu_item.orm import MenuItem
from shaas_common.model.base import BaseRepository
from shaas_common.model.order.orm import Order, OrderEntry


class OrderRepository(BaseRepository):
    model = Order

    async def cancel_order(self, user_id, event_id):
        q = select(Event.owner_id).where(Event.id == event_id)
        owner_id = await self._first(q)

        order_list = await self.get_order_list(event_id, user_id)
        for _, item, count in order_list:
            if item.id == 0:
                q = update(Coupon).where(Coupon.user_id == user_id, Coupon.owner_id == owner_id).values(count=Coupon.count + count)
                await self._session.execute(q)
                break

        q = delete(self.model).where(self.model.user_id == user_id, self.model.event_id == event_id)
        await self._session.execute(q)

    async def create_order(self, user_id, event_id, order_data: dict, comment=None):
        await self.cancel_order(user_id, event_id)

        if len(order_data) == 0:
            return

        if not comment:
            comment = None
        else:
            comment = escape_markdown(comment)

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
        q = select([self.model.id, MenuItem, func.sum(OrderEntry.count)])\
            .join(Order)\
            .join(MenuItem)\
            .where(Order.event_id == event_id)
        if user_id:
            q = q.where(Order.user_id == user_id)
        q = q.group_by(self.model.id, MenuItem)
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
