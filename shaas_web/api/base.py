from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ClearBaseModel(BaseModel):
    class Config:
        use_enum_values = True

        json_encoders = {
            datetime: lambda v: int(v.timestamp()),
        }


class BaseResponseModel(ClearBaseModel):
    created: Optional[datetime] = None
    updated: Optional[datetime] = None

    id: int
