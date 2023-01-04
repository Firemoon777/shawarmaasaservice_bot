from shaas_common.exception.api import ForbiddenError
from shaas_common.model import Token
from shaas_common.storage import Storage


async def is_token_valid(token: str) -> Token:
    if not token:
        raise ForbiddenError()

    s = Storage()

    async with s:
        token_obj: Token = await s.token.get_by_token(token)
        if token_obj.token != token:
            raise ForbiddenError()

    return token_obj
