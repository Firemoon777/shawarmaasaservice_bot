from typing import List

from sqlalchemy import select, desc, update

from shaas_web.model.base.repository import BaseRepository
from shaas_web.model.event.orm import Event, EventState


class EventRepository(BaseRepository):
    model = Event

    async def get_current(self, chat_id):
        """
        Search for current running event
        """
        q = select(self.model).where(self.model.chat_id == chat_id, Event.state != EventState.finished)
        return await self._first(q)

    async def get_last_finished(self, chat_id) -> Event:
        q = select(self.model)\
            .where(self.model.chat_id == chat_id, Event.state == EventState.finished)\
            .order_by(desc(self.model.id))
        return await self._first(q)

    async def stop_event(self, chat_id):
        q = update(self.model).where(self.model.chat_id == chat_id).values(state=EventState.finished)
        await self._session.execute(q)

    async def get_by_poll(self, poll_id):
        q = select(self.model).where(self.model.poll_id == poll_id)
        return await self._first(q)

    async def get_active(self) -> List[Event]:
        q = select(self.model).where(self.model.state == EventState.collecting_orders)
        return await self._as_list(q)

    async def get_active_for_owner(self, owner_id) -> List[Event]:
        q = select(self.model).where(self.model.state != EventState.finished, self.model.owner_id == owner_id)
        return await self._as_list(q)
