from telegram import Update
from telegram.ext import CallbackContext, filters, MessageHandler
from telegram.helpers import mention_markdown

from shaas_web.model import Event, EventState
from shaas_web.model.storage import Storage


async def list(update: Update, context: CallbackContext):
    s = Storage()
    async with s:
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

            comment = await s.order.get_comment(event.id, user_id)
            if comment:
                comment_str = f"\n- {comment}"
            else:
                comment_str = ""

            output.append(f"{mention}:\n" + "\n".join(tmp) + comment_str)

        await update.message.reply_text(
            text="\n\n".join(output),
            parse_mode="markdown"
        )


list_handler = MessageHandler(filters.Text(["Список"]) & filters.ChatType.GROUPS, list)