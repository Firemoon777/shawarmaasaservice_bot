from telegram import Update
from telegram.ext import CallbackContext, PollAnswerHandler

from shaas_common.model import Event, EventState, Order
from shaas_common.poll import close_poll_if_necessary
from shaas_common.session import SessionLocal


async def handle_poll(update: Update, context: CallbackContext):
    session = SessionLocal()
    event = await Event.get_by_poll(session, update.poll_answer.poll_id)
    if not event:
        return

    if event.state != EventState.collecting_orders:
        return

    skip = {event.skip_option}
    options = set(update.poll_answer.option_ids) - skip

    order_data = {event.poll_options[o]: 1 for o in options}
    await Order.submit_order(session, update.poll_answer.user.id, event.id, order_data)

    await close_poll_if_necessary(session, context.bot, update.poll_answer.poll_id)

poll_handler = PollAnswerHandler(handle_poll)