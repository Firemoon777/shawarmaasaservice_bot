import datetime
import time
from logging import getLogger

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters, CallbackContext, \
    PollAnswerHandler, CallbackQueryHandler

from shaas_old.const import product
from shaas_old.messages import send_forbidden, ask_vote_timeout, send_incorrect_input, ask_slots, ask_order_time, \
    create_poll, send_poll_is_running, close_poll, send_picked_up
from shaas_old.storage import storage_parse_poll, storage_check_slots_exceeded, storage_found_poll, is_poll_running, \
    storage_pop_user
from shaas_old.utils import is_sender_admin, get_orders

logger = getLogger(__name__)

PARSE_POLL_TIMEOUT = 1
PARSE_ORDER_TIME = 2
PARSE_SLOTS = 3


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
    list_handler,
    test1_handler,
    test2_handler
]