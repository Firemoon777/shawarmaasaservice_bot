import csv
import time
from datetime import datetime, timedelta
from io import StringIO

from starlette.background import BackgroundTasks
from telegram import LoginUrl, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError, BadRequest
from telegram.helpers import mention_markdown

from shaas_web.api.base import BaseResponseModel, ClearBaseModel
from shaas_web.api.event.model import EventResponse, CreateEventRequest, OrderResponse, OrderItemResponse, \
    OrderListResponse, OrderEntry, ProlongRequest, ReorderRequest
from shaas_web.exceptions import AlreadyRunningError, NotFoundError
from shaas_web.security import is_admin_in_chat, is_member_in_chat

import logging
from typing import Optional, List, Dict

from fastapi import Depends
from pydantic import BaseModel
from starlette.requests import Request
from telegram._bot import BT

from shaas_common.billing import get_html_price_message
from shaas_web.exceptions import ForbiddenError
from shaas_web.model import MenuItem, Event, EventState, Chat
from shaas_common.notification import Notification
from shaas_web.model.storage import Storage
from shaas_web.bot import get_bot


from fastapi import APIRouter

event_router = APIRouter(prefix="/event", tags=["Event"])


@event_router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, request: Request, bot: BT = Depends(get_bot)):
    s = Storage()
    async with s:
        result: Event = await s.event.get(event_id)
        await is_admin_in_chat(bot, result.chat_id, request.state.user_id, raises=True)
        return EventResponse(**result.__dict__)


@event_router.post("/", response_model=EventResponse)
async def create_event(
        data: CreateEventRequest,
        request: Request,
        bot: BT = Depends(get_bot)
):
    # Запускающий пользователь должен быть админом в этом чате
    await is_admin_in_chat(bot, data.chat_id, request.state.user_id, raises=True)

    s = Storage()
    async with s:
        if await s.event.get_current(data.chat_id):
            raise AlreadyRunningError()

    text = f"Сбор заказов до {data.end_time:%H:%M}"
    if data.available_slots > 0: text += f" или до {data.available_slots} позиций"
    text += f".\nВыдача заказов: {data.order_time_data}"

    order_message = await bot.send_message(
        chat_id=data.chat_id,
        text=text
    )

    additional_message = await bot.send_message(
        chat_id=data.chat_id,
        text="Опроса больше нет. Действия с заказом доступны по кнопкам."
    )

    async with s:
        event = await s.event.create(
            chat_id=data.chat_id,
            owner_id=request.state.user_id,
            order_message_id=order_message.message_id,
            additional_message_id=additional_message.message_id,
            collect_message_id=None,
            menu_id=data.menu_id,
            available_slots=data.available_slots,
            delivery_info=data.order_time_data,
            order_end_time=data.end_time,
            money_message=data.money_msg
        )
        await s.menu_item.renew_leftovers(data.menu_id)

    login = LoginUrl(f"{request.app.settings.bot.base_url}login?event_id={event.id}", request_write_access=True)
    login_lucky = LoginUrl(
        f"{request.app.settings.bot.base_url}login?event_id={event.id}&route=/market/{event.id}/lucky",
        request_write_access=True
    )
    keyboard = [
        [
            InlineKeyboardButton("Заказать", login_url=login)
        ],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await order_message.edit_reply_markup(markup)

    keyboard = [
        [
            InlineKeyboardButton("Отменить заказ", callback_data=f"order_cancel_{event.id}"),
            InlineKeyboardButton("Мне повезёт!", login_url=login_lucky),
        ],
        [
            InlineKeyboardButton("Мне как прошлый раз", callback_data=f"order_repeat_{event.id}"),
        ],
        [
            InlineKeyboardButton(
                "Посмотреть мой заказ",
                url="https://t.me/shawarmaasaservice_bot/menu"
                # callback_data=f"order_show_{event.id}"
            )
        ],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await additional_message.edit_reply_markup(markup)

    try:
        # pin and edit_reply_markup leads to crash on some platforms
        time.sleep(1)
        await order_message.pin()
    except TelegramError:
        pass

    return EventResponse(**event.__dict__)


async def check_poll_exceeded(s: Storage, event) -> bool:
    if event.available_slots <= 0:
        return False

    current_orders = await s.order.get_order_total(event.id)

    return current_orders >= event.available_slots


@event_router.post("/check")
async def check_event(request: Request, bot: BT = Depends(get_bot)):
    if request.state.auth_method != "header":
        raise ForbiddenError()

    s = Storage()

    async with s:
        events: List[Event] = await s.event.get_active()

        for event in events:
            logging.info(f"Event {event.id} -> {event.order_end_time} ({event.actual_order_end_time})")

            order_end_time = event.actual_order_end_time if event.actual_order_end_time else event.order_end_time

            if order_end_time > datetime.now():
                if await check_poll_exceeded(s, event) is False:
                    continue

            logging.info(f"Event {event.id} is about to close")

            order_list = await event_order_list(event.id, request, bot)
            print(order_list)

            await s.order.set_ordered(event.id)

            try:
                await bot.delete_message(
                    chat_id=event.chat_id,
                    message_id=event.additional_message_id
                )
            except:
                pass

            try:
                await bot.edit_message_reply_markup(
                    chat_id=event.chat_id,
                    message_id=event.order_message_id
                )
            except BadRequest:
                pass

            time.sleep(1)

            try:
                await bot.unpin_chat_message(
                    chat_id=event.chat_id,
                    message_id=event.order_message_id
                )
            except TelegramError:
                pass

            keyboard = [
                [InlineKeyboardButton("Я забрал", callback_data=f"order_taken_{event.id}")]
            ]
            markup = InlineKeyboardMarkup(keyboard)

            text = "Прием заказов окончен!\nКак только получите свой заказ -- жмите кнопку!"
            if event.money_message:
                text += f"\n\n{event.money_message}"

            message = await bot.send_message(
                chat_id=event.chat_id,
                text=text,
                reply_markup=markup
            )

            await s.event.update(
                event.id,
                collect_message_id=message.message_id,
                state=EventState.delivery
            )

            try:
                await message.pin()
            except TelegramError:
                pass

            await bot.send_message(
                chat_id=event.chat_id,
                text=order_list.total_order(),
                parse_mode="markdown"
            )


@event_router.get("/{event_id}/menu")
async def get_event_menu(
        event_id: int,
        request: Request,
        bot: BT = Depends(get_bot)
):
    s = Storage()
    async with s:
        event: Event = await s.event.get(event_id)
        if not event:
            raise ForbiddenError()

        menu: List[MenuItem] = await s.menu_item.get_items(event.menu_id)

        coupons_count: int = await s.coupon.get_coupons(event.owner_id, request.state.user_id)
        if coupons_count:
            coupon: MenuItem = await s.menu_item.get(0)

    if coupons_count:
        # outside ORM transaction
        coupon.leftover = coupons_count
        menu.insert(0, coupon)

    member = await bot.get_chat_member(chat_id=event.chat_id, user_id=request.state.user_id)
    if not member:
        raise ForbiddenError()

    return {
        "event": EventState(event.state).name,
        "menu": menu
    }


class OrderRequest(BaseModel):
    order: Dict[int, int]
    comment: Optional[str] = ""


@event_router.post("/{event_id}/order")
async def place_order(
        event_id: int,
        order: OrderRequest,
        request: Request,
        bot: BT = Depends(get_bot)
):
    s = Storage()
    order_data = dict()
    used_coupons = order.order[0] if 0 in order.order else 0
    async with s:
        event: Event = await s.event.get(event_id)
        user: Chat = await s.chat.get(request.state.user_id)

        if not event:
            raise ForbiddenError()

        if event.state != EventState.collecting_orders:
            raise ForbiddenError()

        for key_id, value in order.order.items():
            key = await s.menu_item.get(key_id)
            order_data[key] = value

        coupons_count: int = await s.coupon.get_coupons(event.owner_id, request.state.user_id)
        assert used_coupons <= coupons_count
        await s.coupon.update_coupon_count(event.owner_id, request.state.user_id, coupons_count - used_coupons)

        await s.order.create_order(request.state.user_id, event.id, order_data, order.comment)

        my_order = await show_my_order(event_id, request)
        for entry in my_order.order:
            key = await s.menu_item.get(entry.id)
            if key not in order_data:
                order_data[key] = 0

            order_data[key] += entry.count

    msg = "Заказ принят!\n\n" + get_html_price_message(order_data, my_order.comment)

    try:
        await Notification(user, bot).send_message(msg, parse_mode="html")
    except Exception as e:
        logging.warning(f"Unable to send message to {request.state.user_id}, reason: {e}")
        return {"status": "ok", "error": "bot"}

    return {"status": "ok"}


@event_router.get("/{event_id}/my", response_model=OrderResponse)
async def show_my_order(event_id: int, request: Request):
    s = Storage()

    async with s:
        event = await s.event.get(event_id)

        if not event:
            raise NotFoundError()

        order_list = await s.order.get_orders(event.id, request.state.user_id)

        result = OrderResponse()
        for order, chat, item, order_entry in order_list:
            if order_entry.count == 0:
                continue

            result.comment = order.comment
            result.order.append(OrderItemResponse(
                count=order_entry.count,
                is_ordered=order_entry.is_ordered,
                **item.__dict__
            ))

    return result


async def background_check(event_id, bot: BT = Depends(get_bot)):
    s = Storage()

    async with s:
        event = await s.event.get(event_id)
        result = await s.order.get_pending(event_id)

        if result:
            return

        # stat_chat_id = -1001569537280
        # # stat_chat_id = event.chat_id
        # year_usage: List[MenuItem, int] = await s.order.get_current_year_statistic(stat_chat_id)
        # year_usage.sort(key=lambda x: x[1], reverse=True)
        # print(year_usage)
        #
        # year_event_usage: Dict[str, List[Tuple[MenuItem, int]]] = await s.order.get_current_year_statistic_for_all_events(stat_chat_id)
        #
        # labels = []
        # items_name = [item.name for item, _ in year_usage]
        # counts = {
        #     name: list() for name in items_name
        # }
        #
        # ylim = 0
        # for d, items in year_event_usage.items():
        #     tmp = 0
        #
        #     labels.append(d)
        #     for name in items_name:
        #         counts[name].append(0)
        #
        #     for item, count in items:
        #         counts[item.name][-1] = count
        #         tmp += count
        #     ylim = max(ylim, tmp)
        #
        # width = 0.6  # the width of the bars: can also be len(x) sequence
        # bottom = np.zeros(len(labels))
        #
        # fig, ax = plt.subplots(figsize=(8, 4.5), dpi=150)
        # for item_name, item_count in counts.items():
        #     p = ax.bar(
        #         labels,
        #         item_count,
        #         width,
        #         label=item_name,
        #         bottom=bottom,
        #
        #     )
        #     bottom += item_count
        #
        #     # ax.bar_label(p, label_type='center')
        #
        # ax.set_ylim(0, ylim + 10)
        # for tick in ax.get_xticklabels():
        #     tick.set_rotation(90)
        #
        # box = ax.get_position()
        # ax.set_position([box.x0, box.y0 + 0.1, box.width * 0.75, box.height-0.1])
        #
        # # Put a legend to the right of the current axis
        # ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        #
        # ax.set_title('Статистика')
        # ax.grid(axis="y")
        # ax.text(0, 123, 123, ha='center', weight='bold', color='black')
        # ax.text(1, 4567, 4567, ha='center', weight='bold', color='black')
        #
        # buf = BytesIO()
        # plt.savefig(buf, format="png")
        # buf.seek(0)
        #
        # await context.bot.send_photo(
        #     chat_id=event.chat_id,
        #     photo=buf,
        #     caption="Все отметились, что забрали заказ\n\n" + event.money_message,
        #     disable_notification=True
        # )
        #
        # return
        total = await s.order.get_order_list_extended(event.id)

        today = f"{event.order_end_time.year}-{event.order_end_time.month:02}-{event.order_end_time.day:02}"
        string_io = StringIO()
        fieldnames = ["sum", "date", "login", "user_id", "name"]
        writer = csv.DictWriter(string_io, fieldnames=fieldnames)
        writer.writeheader()
        for order, chat, item_sum in total:
            writer.writerow({
                "sum": item_sum,
                "date": str(today),
                "login": chat.username,
                "user_id": chat.id,
                "name": chat.name
            })

        await bot.send_document(
            event.owner_id,
            document=string_io.getvalue().encode("utf-8"),
            filename=f"{today}-shaas-{event.id}.csv"
        )

        await bot.unpin_chat_message(
            chat_id=event.chat_id,
            message_id=event.collect_message_id
        )

        time.sleep(1)

        await bot.edit_message_reply_markup(
            chat_id=event.chat_id,
            message_id=event.collect_message_id,
            reply_markup=None
        )

        ## Тут сбщ

        await s.event.update(
            event.id,
            state=EventState.finished
        )


@event_router.post("/{event_id}/my")
async def take_order(event_id: int, request: Request, background_tasks: BackgroundTasks, bot: BT = Depends(get_bot)):
    s = Storage()

    async with s:
        event = await s.event.get(event_id)

        if not event:
            raise NotFoundError()

        await s.order.take_order(event.id, request.state.user_id)

    await background_check(event_id, bot)
    return await show_my_order(event_id, request)


@event_router.delete("/{event_id}/my")
async def cancel_my_order(event_id: int, request: Request):
    s = Storage()

    async with s:
        event = await s.event.get(event_id)

        if not event:
            raise NotFoundError()

        await s.order.cancel_order(request.state.user_id, event.id)
    return True


@event_router.post("/{event_id}/repeat")
async def order_previous(event_id: int, request: Request, bot: BT = Depends(get_bot)):
    s = Storage()

    async with s:
        event: Event = await s.event.get(event_id)
        user: Chat = await s.chat.get(request.state.user_id)

        if not event:
            raise NotFoundError()

        previous_order = await s.order.get_previous_order(
            request.state.user_id,
            current_event_id=event.id,
            current_chat_id=event.chat_id
        )
        user_order_list = await s.order.get_order_list(previous_order.event_id, request.state.user_id)
        comment = await s.order.get_comment(event.id, request.state.user_id)

    if not user_order_list:
        return await show_my_order(event_id, request)

    new_user_order_list = {}
    for _, item, count in user_order_list:
        if item.id == 0:
            continue

        new_user_order_list[item] = count

    async with s:
        await s.order.create_order(
            request.state.user_id,
            event.id,
            new_user_order_list,
            comment
        )

    return await show_my_order(event_id, request)


@event_router.get("/{event_id}/list", response_model=OrderListResponse)
async def event_order_list(event_id: int, request: Request, bot: BT = Depends(get_bot)):
    s = Storage()

    async with s:
        event: Event = await s.event.get(event_id)
        if not event:
            raise NotFoundError()

        await is_member_in_chat(bot, event.chat_id, request.state.user_id, raises=True)

        order_list = await s.order.get_orders(event.id)

        order_dict: Dict[int, OrderEntry] = dict()
        for order, chat, item, order_entry in order_list:
            if chat.id not in order_dict:
                order_dict[chat.id] = OrderEntry(
                    user_id=chat.id,
                    username=chat.username,
                    name=chat.name,
                    is_taken=order.is_taken,
                )

            order_dict[chat.id].comment = order.comment
            order_dict[chat.id].order.append(OrderItemResponse(
                count=order_entry.count,
                is_ordered=order_entry.is_ordered,
                **item.__dict__
            ))

    return OrderListResponse(orders=list(order_dict.values()))


@event_router.post("/{event_id}/prolong", response_model=EventResponse)
async def prolong_order(
        event_id:int,
        data: ProlongRequest,
        request: Request,
        bot: BT = Depends(get_bot),
):
    s = Storage()
    async with s:
        event: Event = await s.event.get(event_id)

        assert event.owner_id == request.state.user_id

        if event.state != EventState.collecting_orders:
            raise ForbiddenError()

        event.actual_order_end_time = data.time

        await bot.send_message(
            chat_id=event.chat_id,
            text=f"Новое время закрытия заказов: {event.actual_order_end_time}"
        )

    return EventResponse(**event.__dict__)


@event_router.post("/{event_id}/reorder", response_model=EventResponse)
async def reorder(
        event_id: int,
        data: ReorderRequest,
        request: Request,
        bot: BT = Depends(get_bot)
):
    s = Storage()
    async with s:
        event: Event = await s.event.get(event_id)

        assert event.owner_id == request.state.user_id

        users = set()
        missing_item = []
        for item_id, value in data.entries.items():
            if value:
                continue

            item: MenuItem = await s.menu_item.get(item_id)
            item.leftover = 0
            missing_item.append(f"- {item.name}")

            ids = await s.order.get_order_by_choice(event_id, item.id)

            for user_id in ids:
                member = await bot.get_chat_member(chat_id=event.chat_id, user_id=user_id)
                users.add(mention_markdown(user_id, member.user.full_name))

            await s.order.zero_count(event_id, item_id)

        await bot.delete_message(chat_id=event.chat_id, message_id=event.collect_message_id)

        event.state = EventState.collecting_orders
        event.actual_order_end_time = data.time
        event.collect_message_id = None

        if users:
            missing_item_str = "\n".join(missing_item)
            users_str = ", ".join(users)
            text = (
                f"ТРЕБУЕТСЯ ДЕЙСТВИЕ\n"
                f"\n"
                f"Внимание! Следующих позиций нет:\n"
                f"{missing_item_str}\n"
                f"\n"
                f"Пользователи {users_str} должны перезаказать или останутся без еды!\n"
                f"Заказы открыты до {event.actual_order_end_time.hour:02}:{event.actual_order_end_time.minute:02}"
            )
        else:
            text = (
                "Приём заказов продлен.\n"
                f"Заказы открыты до {event.actual_order_end_time.hour:02}:{event.actual_order_end_time.minute:02}"
            )

        login = LoginUrl(f"{request.app.settings.bot.base_url}login?event_id={event.id}")
        keyboard = [
            [
                InlineKeyboardButton("Заказать", login_url=login)
            ],
        ]
        markup = InlineKeyboardMarkup(keyboard)
        order_message = await bot.send_message(chat_id=event.chat_id, text=text, parse_mode="markdown", reply_markup=markup)
        await order_message.pin(disable_notification=True)

        event.order_message_id = order_message.message_id

    return EventResponse(**event.__dict__)