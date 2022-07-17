from telegram import Update
from telegram.ext import CallbackContext, PollAnswerHandler

from shaas_common.model.event.orm import EventState
from shaas_common.poll import close_poll_if_necessary
from shaas_common.session import SessionLocal
from shaas_common.storage import Storage


async def handle_poll(update: Update, context: CallbackContext):
    s = Storage()
    event = await s.event.get_by_poll(update.poll_answer.poll_id)
    if not event:
        return

    if event.state != EventState.collecting_orders:
        return

    skip = {event.skip_option}
    options = set(update.poll_answer.option_ids)

    if options == skip:
        return

    options -= skip

    order_data = dict()
    for option in options:
        item_id = event.poll_options[option]
        item = await s.menu_item.get(item_id)
        order_data[item] = 1

    await s.order.create_order(update.poll_answer.user.id, event.id, order_data)
    await s.commit()

    await close_poll_if_necessary(s, context.bot, update.poll_answer.poll_id)

poll_handler = PollAnswerHandler(handle_poll)