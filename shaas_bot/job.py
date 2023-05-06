from telegram.ext import CallbackContext

from shaas_bot.utils import core_request


async def cron_check(context: CallbackContext):
    await core_request(context, "/event/check", method="post")
