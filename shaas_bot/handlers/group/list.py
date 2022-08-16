from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, filters, MessageHandler
from telegram.helpers import mention_markdown

from shaas_bot.utils import is_group_chat, is_sender_admin
from shaas_common.model import Event, EventState
from shaas_common.storage import Storage


async def list(update: Update, context: CallbackContext):
    s = Storage()
    event: Event = await s.event.get_current(update.message.chat_id)
    if not event:
        await update.message.reply_text("Событие еще не началось или уже закончилось")
        return

    if event.state == EventState.collecting_orders:
        await update.message.reply_text("Заказы только собираются")
        return

    result = await s.order.get_pending(event.id)

    user_data = dict()
    for name, user_id, count in result:
        if user_id not in user_data:
            user_data[user_id] = dict()

        user_data[user_id][name] = count

    output = []
    for user_id, order in user_data.items():
        member = await context.bot.getChatMember(update.message.chat_id, user_id)
        mention = mention_markdown(user_id, member.user.full_name)
        tmp = []
        for name, count in order.items():
            tmp.append(f"{count}x {name}")
        output.append(f"{mention}:\n" + "\n".join(tmp))

    await update.message.reply_text(
        text="\n\n".join(output),
        parse_mode="markdown"
    )


list_handler = MessageHandler(filters.Text(["Список"]) & filters.ChatType.GROUPS, list)