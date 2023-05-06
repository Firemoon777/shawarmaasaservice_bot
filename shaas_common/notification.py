from telegram._bot import BT

from shaas_web.model import Chat


class Notification:
    _user: Chat
    _bot: BT

    def __init__(self, user: Chat, bot: BT):
        self._bot = bot
        self._user = user

    async def send_message(self, msg, parse_mode=None):
        if not self._user.send_direct_messages:
            return

        await self._bot.send_message(chat_id=self._user.id, text=msg, parse_mode=parse_mode)

