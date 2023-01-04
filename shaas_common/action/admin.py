from typing import List

from telegram import Bot

from shaas_common.model import Chat
from shaas_common.storage import Storage


async def get_controlled_chats(bot: Bot, user_id: int) -> List[Chat]:
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

