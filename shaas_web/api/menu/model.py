from typing import List, Optional

from shaas_web.api.base import BaseResponseModel, ClearBaseModel


class MenuItem(BaseResponseModel):
    name: str
    price: float

    description: Optional[str] = None
    proteins: Optional[float] = None
    fats: Optional[float] = None
    carbohydrates: Optional[float] = None
    calories: Optional[float] = None

    picture: Optional[str] = None

    leftover: int


class MenuItemListResponse(ClearBaseModel):
    menu: List[MenuItem] = list()