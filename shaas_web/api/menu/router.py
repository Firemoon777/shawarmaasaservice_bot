from fastapi import APIRouter
from starlette.requests import Request

from shaas_web.api.menu.model import MenuItemListResponse, MenuItem
from shaas_web.model.storage import Storage

menu_router = APIRouter(prefix="/menu", tags=["Menu"])


# @menu_router.get("/{menu_id}", response_model=MenuItemListResponse)
# async def get_menu(menu_id: int, request: Request):
#     s = Storage()
#
#     async with s:
#         menu = await s.menu_item.get_items(menu_id)
#
#     return MenuItemListResponse(
#         menu=[MenuItem(**item.__dict__) for item in menu]
#     )