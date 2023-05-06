from typing import List

from telegram import ChatMember
from telegram._bot import BT

from shaas_web.exceptions import ForbiddenError


async def is_admin_in_chat(bot: BT, chat_id: int, user_id: int, raises=False):
    admins: List[ChatMember] = await bot.get_chat_administrators(chat_id)
    is_admin = False
    for member in admins:
        if member.user.id == user_id:
            is_admin = True
            break

    if raises and not is_admin:
        raise ForbiddenError()

    return is_admin
