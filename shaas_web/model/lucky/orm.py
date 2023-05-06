from sqlalchemy import Column, BigInteger, String, Boolean, ForeignKey, Integer, DateTime
from sqlalchemy.sql import expression

from shaas_web.model.base.orm import BaseTable


class LuckyAttempt(BaseTable):
    __tablename__ = "shaas_lucky_attempt"

    user_id = Column(BigInteger, ForeignKey("shaas_chat.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("shaas_event.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("shaas_menu_item.id"), nullable=False)

    accepted = Column(Boolean, server_default=expression.false(), default=False)
