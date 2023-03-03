from typing import *

from shaas_common.model import MenuItem


def calc_price(order_data: Dict[MenuItem, int]) -> Tuple[Dict[MenuItem, int], Dict[MenuItem, int]]:
    used_coupons = 0

    paid_items_list = []
    free_items_list = []
    for item, count in order_data.items():
        if item.id == 0:
            used_coupons += count
        else:
            paid_items_list.extend([item] * count)

    paid_items_list.sort(key=lambda x: x.price, reverse=True)

    for i in range(used_coupons):
        free_items_list.append(paid_items_list.pop(0))

    paid_items_dict = dict()
    for item in paid_items_list:
        if item not in paid_items_dict:
            paid_items_dict[item] = 0
        paid_items_dict[item] += 1

    free_items_dict = dict()
    for item in free_items_list:
        if item not in free_items_dict:
            free_items_dict[item] = 0
        free_items_dict[item] += 1

    return paid_items_dict, free_items_dict


def get_html_price_message(order_data: Dict[MenuItem, int], comment: Optional[str] = None) -> str:
    msg = ""

    paid_items_dict, free_items_dict = calc_price(order_data)

    total = 0
    for item, count in paid_items_dict.items():
        total += count*item.price
        msg += f"{count}x {item.name} - {count*item.price} р.\n"

    for item, count in free_items_dict.items():
        msg += f"{count}x {item.name} - <s>{count * item.price} р.</s> 0 р.\n"

    msg += f"\nИтого: {total} р."

    if comment:
        msg += f'\n\nКомментарий:\n{comment.replace("<", "&lt;").replace(">", "&gt;")}'

    return msg


def get_short_price_message(order_data: Dict[MenuItem, int], comment: Optional[str] = None) -> str:
    msg = ""

    paid_items_dict, free_items_dict = calc_price(order_data)

    total = 0
    for item, count in paid_items_dict.items():
        total += count * item.price
        msg += f"{count}x {item.name} - {count * item.price} р.\n"

    for item, count in free_items_dict.items():
        msg += f"{count}x {item.name} - 0 р.\n"

    msg += f"\nИтого: {total} р."

    if comment:
        msg += f'\n\nКомментарий:\n{comment.replace("<", "&lt;").replace(">", "&gt;")}'

    return msg