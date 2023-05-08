from typing import List

from telegram import ChatMember
from telegram._bot import BT

from shaas_web.exceptions import ForbiddenError
from shaas_web.model import Chat
from shaas_web.model.storage import Storage


async def is_admin_in_chat(bot: BT, chat_id: int, user_id: int, raises=False):
    if user_id == 0:
        return True

    admins: List[ChatMember] = await bot.get_chat_administrators(chat_id)
    is_admin = False
    for member in admins:
        if member.user.id == user_id:
            is_admin = True
            break

    if raises and not is_admin:
        raise ForbiddenError()

    return is_admin


async def is_member_in_chat(bot: BT, chat_id: int, user_id: int, raises=False):
    if user_id == 0:
        return True

    member: ChatMember = await bot.get_chat_member(chat_id, user_id)

    if member.status not in [member.MEMBER, member.ADMINISTRATOR, member.OWNER]:
        if raises:
            raise ForbiddenError()

        return False

    return True


async def get_controlled_chats(bot: BT, user_id: int) -> List[Chat]:
    """
    Выдает список каналов, в которых пользователь является админом
    """
    s = Storage()
    result = list()

    async with s:
        for chat in await s.chat.all():
            if chat.id > 0:
                continue

            member = await bot.getChatMember(chat_id=chat.id, user_id=user_id)
            if member.status not in [member.ADMINISTRATOR, member.OWNER]:
                continue

            result.append(chat)

    return result
