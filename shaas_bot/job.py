from telegram.ext import CallbackContext

from shaas_common.poll import close_events_if_necessary


async def load_jobs(context: CallbackContext):
    print(context.bot.name)

    context.job_queue.run_repeating(
        close_events_if_necessary,
        10,
        name=f"scheduler"
    )