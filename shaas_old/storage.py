from typing import Optional

from telegram import Message, Update
from telegram.ext import CallbackContext


def storage_init_with_poll(context: CallbackContext, message: Message, max_slots: int):
    if message.poll is None:
        raise Exception("No poll found!")

    context.bot_data[message.chat_id] = {
        "chat_id": message.chat_id,
        "message_id": message.message_id,
        "poll_id": message.poll.id,
        "answers": 0,
        "users": dict(),
        "available_slots": max_slots,
        "is_running": True
    }


def storage_found_poll(context: CallbackContext, poll_id) -> Optional[int]:
    for chat_id, payload in context.bot_data.items():
        if payload.get("poll_id") == poll_id:
            return chat_id

    return None


def storage_parse_poll(context: CallbackContext, update: Update):
    answer = update.poll_answer
    poll_id = answer.poll_id

    chat_id = storage_found_poll(context, poll_id)
    if chat_id is None:
        return

    options = list(set(answer.option_ids) - {9})
    options.sort()

    context.bot_data[chat_id]["answers"] += len(options)
    context.bot_data[chat_id]["users"][update.poll_answer.user.id] = {
        "name": update.poll_answer.user.full_name,
        "username": update.poll_answer.user.username,
        "options": options
    }


def storage_check_slots_exceeded(context: CallbackContext, chat_id) -> bool:
    if context.bot_data[chat_id]["available_slots"] <= 0:
        return False

    if context.bot_data[chat_id]["available_slots"] > context.bot_data[chat_id]["answers"]:
        return False

    return True


def storage_pop_user(context: CallbackContext, chat_id, user_id):
    if chat_id not in context.bot_data:
        return None

    users = context.bot_data[chat_id]["users"]

    if user_id not in users:
        return None

    user = users[user_id]
    del users[user_id]

    return user


def is_poll_running(context: CallbackContext, chat_id) -> bool:
    return context.bot_data.get(chat_id, {}).get("is_running", False)