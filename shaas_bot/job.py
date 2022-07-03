import datetime

from sqlalchemy import select
from telegram.ext import CallbackContext

from shaas_bot.handlers.event_handler import close_poll_job
from shaas_common.model import Event, EventState
from shaas_common.session import SessionLocal


async def load_jobs(context: CallbackContext):
    session = SessionLocal()

    q = select(Event).where(Event.state == EventState.collecting_orders)
    result = await session.execute(q)
    events = list(result.scalars())

    for event in events:
        job_context = dict(
            poll_id=event.poll_id
        )

        context.job_queue.run_once(
            close_poll_job,
            event.order_end_time - datetime.datetime.now(),
            chat_id=event.chat_id,
            context=job_context,
            name=f"{event.chat_id}"
        )