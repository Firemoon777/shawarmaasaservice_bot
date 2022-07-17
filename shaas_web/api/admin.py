from fastapi import APIRouter, Depends
from sqlalchemy import select
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from shaas_common.model import Chat
from shaas_common.session import get_db
from shaas_web.bot import get_bot

admin_router = APIRouter(prefix="/admin")

templates = Jinja2Templates(directory="templates")


@admin_router.get("/")
async def admin_menu(
    request: Request,
    db=Depends(get_db),
    bot=Depends(get_bot)
):
    data = {
        "request": request
    }
    return templates.TemplateResponse("admin.html", data)