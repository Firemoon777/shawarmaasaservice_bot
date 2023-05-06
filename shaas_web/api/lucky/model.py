from typing import Optional

from shaas_web.api.base import BaseResponseModel, ClearBaseModel


class LuckyAttemptRequest(ClearBaseModel):
    event_id: int


class MenuItemResponse(BaseResponseModel):
    name: str
    price: float

    description: Optional[str] = None
    proteins: Optional[float] = None
    fats: Optional[float] = None
    carbohydrates: Optional[float] = None
    calories: Optional[float] = None

    picture: Optional[str] = None


class LuckyResponse(BaseResponseModel):
    item: MenuItemResponse


class LuckyAttemptAcceptance(ClearBaseModel):
    event_id: int
    item_id: int
