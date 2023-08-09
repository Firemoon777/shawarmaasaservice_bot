import datetime
import hmac
import hashlib
import uuid
from typing import Optional

import requests
from fastapi import APIRouter, Cookie, HTTPException
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import Response

from shaas_web.model import Token
from shaas_web.model.storage import Storage

login_router = APIRouter(prefix="/login", tags=["Login"])


class LoginModel(BaseModel):
    event_id: Optional[int]
    id: int
    first_name: Optional[str]
    last_name: Optional[str]
    photo_url: Optional[str]
    username: Optional[str]
    auth_date: int
    hash: str
    lucky: bool = False


@login_router.post("/")
async def check(request: Request, response: Response, data: LoginModel, shaas_token: Optional[str] = Cookie(default=None, alias="token")):
    """
    https://core.telegram.org/widgets/login
    """
    s = Storage()

    if shaas_token:
        async with s:
            entry = await s.token.get_by_token(shaas_token)
            if entry and entry.user_id == data.id and entry.expires_in > datetime.datetime.now():
                return {"status": "ok"}

    bot_token: str = request.app.settings.bot.token

    data_str = str()
    keys = list(data.__fields__.keys())
    keys.sort()

    for key in keys:
        value = getattr(data, key)
        if not value:
            continue

        if key in ["hash", "event_id", "lucky"]:
            continue

        data_str += f"{key}={value}\n"

    data_str = data_str.strip()

    secret_key = hashlib.sha256(bot_token.encode("utf-8")).digest()
    computed = hmac.new(
        key=secret_key,
        msg=data_str.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    if data.hash != computed:
        raise HTTPException(status_code=403, detail="Invalid login")

    expires_in = datetime.datetime.now() + datetime.timedelta(days=7)
    async with s:
        await s.chat.update_chat(data.id, f"{data.first_name} {data.last_name}".strip(), data.username)

        token: Token = await s.token.create(
            user_id=data.id,
            token=str(uuid.uuid4()),
            expires_in=expires_in
        )
    response.set_cookie("token", token.token, httponly=True, expires=int(expires_in.timestamp()))

    return {
        "status": "renewed"
    }


class WebAppLoginModel(BaseModel):
    initData: str
    user_id: int
    hash: str


@login_router.post("/webapp")
async def check(request: Request, response: Response, data: WebAppLoginModel):
    s = Storage()

    bot_token: str = request.app.settings.bot.token

    query_dict = dict()
    for entry in data.initData.split("&"):
        key, value = entry.split("=")
        if key == "hash":
            continue

        query_dict[key] = value

    print(requests.utils.unquote(data.initData))
    keys = list(query_dict.keys())
    keys.sort()
    data_check_list = [f"{key}={requests.utils.unquote(query_dict[key])}" for key in keys]
    data_check_string = "\n".join(data_check_list)

    secret_key = hmac.new(
        key=b"WebAppData",
        msg=bot_token.encode("utf-8"),
        digestmod=hashlib.sha256
    ).digest()
    computed = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    if data.hash != computed:
        print(f"Expected:   {data.hash}")
        print(f"Calculated: {computed}")
        raise HTTPException(status_code=403, detail="Invalid login")

    expires_in = datetime.datetime.now() + datetime.timedelta(days=7)
    async with s:
        # await s.chat.update_chat(data.id, f"{data.first_name} {data.last_name}".strip(), data.username)

        token: Token = await s.token.create(
            user_id=data.user_id,
            token=str(uuid.uuid4()),
            expires_in=expires_in
        )
    response.set_cookie("token", token.token, httponly=True, expires=int(expires_in.timestamp()))

    return {
        "status": "renewed"
    }