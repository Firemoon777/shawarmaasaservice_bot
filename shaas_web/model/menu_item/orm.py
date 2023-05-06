from sqlalchemy import Column, Integer, String, ForeignKey, Float, BigInteger

from shaas_web.model.base import BaseTable


class MenuItem(BaseTable):
    __tablename__ = "shaas_menu_item"

    menu_id = Column(BigInteger, ForeignKey("shaas_menu.id"), nullable=False)

    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)

    description = Column(String, nullable=True)
    proteins = Column(Float, nullable=True)
    fats = Column(Float, nullable=True)
    carbohydrates = Column(Float, nullable=True)
    calories = Column(Float, nullable=True)

    picture = Column(String, nullable=True)

    leftover = Column(Integer, default=100, server_default="100")

    category = Column(String, default="default", server_default="default")
