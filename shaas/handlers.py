import datetime
import time
from logging import getLogger

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters, CallbackContext, \
    PollAnswerHandler, CallbackQueryHandler

from shaas.const import product
from shaas.messages import send_forbidden, ask_vote_timeout, send_incorrect_input, ask_slots, ask_order_time, \
    create_poll, send_poll_is_running, close_poll, send_picked_up
from shaas.storage import storage_parse_poll, storage_check_slots_exceeded, storage_found_poll, is_poll_running, \
    storage_pop_user
from shaas.utils import is_sender_admin, get_orders

logger = getLogger(__name__)

PARSE_POLL_TIMEOUT = 1
PARSE_ORDER_TIME = 2
PARSE_SLOTS = 3


async def start(update: Update, context: CallbackContext):
    context.user_data.clear()

    admin = await is_sender_admin(update, context)
    if not admin:
        await send_forbidden(update, context)
        return ConversationHandler.END

    if is_poll_running(context, update.message.chat_id):
        await send_poll_is_running(update, context)
        return ConversationHandler.END

    await ask_vote_timeout(update, context)

    return PARSE_POLL_TIMEOUT


async def parse_poll_timeout(update: Update, context: CallbackContext):
    data = update.message.text.strip()
    try:
        h, m = data.split(":", 1)
        h = int(h)
        m = int(m)
        datetime.datetime.now().replace(hour=h, minute=m)
    except ValueError:
        await send_incorrect_input(update, context)
        return PARSE_POLL_TIMEOUT

    context.user_data["end_time"] = (h, m)
    await ask_order_time(update, context)

    return PARSE_ORDER_TIME


async def parse_order_time(update: Update, context: CallbackContext):
    data = update.message.text.strip()
    context.user_data["order_time"] = data
    await ask_slots(update, context)

    return PARSE_SLOTS


async def parse_slots(update: Update, context: CallbackContext):
    try:
        context.user_data["slot"] = int(update.message.text)
    except ValueError:
        await send_incorrect_input(update, context)
        return PARSE_SLOTS

    await create_poll(update, context)

    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text(f'Canceled!')
    return ConversationHandler.END


async def handle_poll(update: Update, context: CallbackContext):
    storage_parse_poll(context, update)

    poll_id = update.poll_answer.poll_id
    chat_id = storage_found_poll(context, poll_id)

    if storage_check_slots_exceeded(context, chat_id):
        message_id = context.bot_data[chat_id]["message_id"]
        await close_poll(context, chat_id, message_id)


async def handle_button(update: Update, context: CallbackContext):
    query = update.callback_query
    message = query.message
    chat_id = message.chat_id
    user_id = query.from_user.id

    user = storage_pop_user(context, chat_id, user_id)

    if user is None:
        await query.answer("У вас нет заказа!", show_alert=False)
        return

    order = [f"1x {product[option_id]}" for option_id in user["options"]]
    msg = "Ваш заказ:\n" + "\n".join(order)
    await query.answer(msg, show_alert=True)

    if len(context.bot_data[chat_id]["users"]) == 0:
        time.sleep(1)
        await message.unpin()
        time.sleep(1)
        await message.edit_reply_markup(InlineKeyboardMarkup([]))
        time.sleep(1)
        await send_picked_up(update, context)


async def show_list(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    orders = get_orders(context, chat_id)
    if len(orders) > 0:
        await update.message.reply_text(
            text="Оставшиеся заказы:\n" + "\n".join(orders)
        )
    else:
        await update.message.reply_text(
            text="Все заказы разобрали!"
        )


launch_handler = ConversationHandler(
    entry_points=[CommandHandler("launch", start)],
    states={
        PARSE_POLL_TIMEOUT: [MessageHandler(filters.TEXT, parse_poll_timeout)],
        PARSE_ORDER_TIME: [MessageHandler(filters.TEXT, parse_order_time)],
        PARSE_SLOTS: [MessageHandler(filters.TEXT, parse_slots)]
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)

poll_handler = PollAnswerHandler(handle_poll)
query_handler = CallbackQueryHandler(handle_button)
list_handler = CommandHandler("list", show_list)

all_handlers = [
    launch_handler,
    poll_handler,
    query_handler,
    list_handler
]