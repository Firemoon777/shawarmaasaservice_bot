import datetime

from telegram.ext import CallbackContext

from shaas_bot.handlers.group.launch import close_poll_job
from shaas_common.storage import Storage


async def load_jobs(context: CallbackContext):
    s = Storage()

    events = await s.event.get_active()

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