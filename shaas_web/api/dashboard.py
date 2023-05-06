from fastapi import APIRouter
from starlette.requests import Request

from shaas_web.api.base import BaseResponseModel

dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


class WhoResponse(BaseResponseModel):
    user_id: int
    auth_method: str


@dashboard_router.get("/who", response_model=WhoResponse)
async def who(request: Request):
    return WhoResponse(
        user_id=request.state.user_id,
        auth_method=request.state.auth_method
    )
