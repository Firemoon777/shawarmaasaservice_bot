from sqlalchemy import select

from shaas_common.model.base.repository import BaseRepository
from shaas_common.model.chat.orm import Chat


class ChatRepository(BaseRepository):
    model = Chat