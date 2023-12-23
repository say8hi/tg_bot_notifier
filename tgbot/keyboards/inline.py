from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import calendar

from tgbot.models.db import Database
from tgbot.messages.inline_buttons import *

admin_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📬Рассылка", callback_data="broadcast")
        ],
        [
            InlineKeyboardButton(text="➕Добавить часовой пояс", callback_data="add_time_zone")
        ],
        [
            InlineKeyboardButton(text="✖️Закрыть", callback_data="close")
        ]
    ]
)

back_admin = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙Назад", callback_data='back_admin')
        ]
    ]
)

back_to_users = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙Назад", callback_data='access_to_bot')
        ]
    ]
)


def add_new_user_menu(user_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅Все верно, добавить", callback_data=f'manage_user:add:{user_id}')
            ],
            [
                InlineKeyboardButton(text="🔙Назад", callback_data='access_to_bot')
            ]
        ]
    )


choose_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✔️Да", callback_data='yes'),
        ],
        [
            InlineKeyboardButton(text="🔙Назад", callback_data='back_admin')
        ]
    ]
)


def inside_user_menu(user_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🗑Удалить", callback_data=f'manage_user:del:{user_id}'),
            ],
            [
                InlineKeyboardButton(text="🔙Назад", callback_data='access_to_bot')
            ]
        ]
    )


def del_user_menu(user_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="↩️Вернуть", callback_data=f'manage_user:add:{user_id}'),
            ],
            [
                InlineKeyboardButton(text="🔙Нет, вернуться к юзерам", callback_data='access_to_bot')
            ]
        ]
    )


async def users_menu():
    users = await Database.users.get(get_all=True)
    keyboard = InlineKeyboardBuilder()
    for user in users:
        keyboard.add(InlineKeyboardButton(text=f"@{user.get('username')}", callback_data=f"user:{user.get('id')}"))
    keyboard.adjust(2, repeat=True)
    keyboard.row(InlineKeyboardButton(text="➕Выдать доступ", callback_data="give_access"))
    keyboard.row(InlineKeyboardButton(text="🔙Назад", callback_data="back_admin"))
    return keyboard.as_markup()


def personal_acc_menu(lang):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=change_time_zone_msg.get(lang), callback_data="change_time_zone:main")
            ],
            [
                InlineKeyboardButton(text=close_btn.get(lang), callback_data="close")
            ]
        ]
    )


def time_zone_menu(time_zones, user):
    keyboard = InlineKeyboardBuilder()
    for record in time_zones:
        keyboard.add(InlineKeyboardButton(
            text=f"{'✅' if user.get('time_zone') == record.get('time_zone') else ''}{record.get('time_zone')}",
            callback_data=f"change_time_zone:{record.get('time_zone')}")
        )
    keyboard.adjust(1, repeat=True)
    keyboard.row(InlineKeyboardButton(text=aks_for_time_zone.get(user.get('lang')), url="https://t.me/say8hi"))
    keyboard.row(InlineKeyboardButton(text=back_button.get(user.get('lang')), callback_data="personal_acc"))
    return keyboard.as_markup()


def inside_notification_menu(notification_id, enabled, lang):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=edit_title_button.get(lang),
                                     callback_data=f"edit_notification:title:{notification_id}"),
                InlineKeyboardButton(text=edit_desc_button.get(lang),
                                     callback_data=f"edit_notification:desc:{notification_id}"),
            ],
            [
                InlineKeyboardButton(text=edit_date_button.get(lang),
                                     callback_data=f"edit_notification:date:{notification_id}"),
                InlineKeyboardButton(text=delete_notification_button.get(lang),
                                     callback_data=f"edit_notification:delete:{notification_id}")
            ],
            [
                InlineKeyboardButton(text=on_notification.get(lang) if enabled == 1 else off_notification.get(lang),
                                     callback_data=f"enable_notification:{notification_id}")
            ],
            [
                InlineKeyboardButton(text=back_button.get(lang),
                                     callback_data="all_notifications")
            ]
        ]
    )


def back_menu(lang: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=back_button.get(lang), callback_data="back_to_main_menu")
            ]
        ]
    )


def agree_menu(lang: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=done_button.get(lang), callback_data="done_adding"),
                InlineKeyboardButton(text=cancel_button.get(lang), callback_data="back_to_main_menu")
            ]
        ]
    )


def back_to_notification_menu(lang):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=back_button.get(lang),
                                     callback_data="all_notifications")
            ]
        ]
    )


async def notification_menu(user_id, lang):
    keyboard = InlineKeyboardBuilder()
    user_notifications = await Database.notifications.get(user_id=user_id)
    for notification in user_notifications:
        keyboard.add(InlineKeyboardButton(text=notification.get("title"),
                                          callback_data=f"notification:{notification.get('id')}"))
    keyboard.adjust(2, repeat=True)
    keyboard.row(InlineKeyboardButton(text=add_notification_button.get(lang),
                                      callback_data="add_notification"))
    keyboard.row(InlineKeyboardButton(text=close_btn.get(lang),
                                      callback_data="close"))
    return keyboard.as_markup()


async def select_date_menu(user, year, month, day):
    keyboard = InlineKeyboardBuilder()
    day_count = calendar.monthrange(int(year), int(month))
    keyboard.row(InlineKeyboardButton(text="⬅️", callback_data=f"add_choose_date:{year}:{int(month) - 1}:{day}:not"),
                 InlineKeyboardButton(text=month_dict.get(int(month)).get(user.get('lang')), callback_data=f"..."),
                 InlineKeyboardButton(text="➡️️", callback_data=f"add_choose_date:{year}:{int(month) + 1}:{day}:not"))

    keyboard.row(InlineKeyboardButton(text="1", callback_data=f"add_choose_date:{year}:{month}:{1}:not"))
    for i in range(2, day_count[1] + 1):
        if i == int(day):
            keyboard.add(InlineKeyboardButton(text=f"✅{i}", callback_data=f"..."))
            continue
        keyboard.add(InlineKeyboardButton(text=str(i), callback_data=f"add_choose_date:{year}:{month}:{i}:not"))

    # keyboard.adjust(7, repeat=True)
    keyboard.adjust(3, 7)
    keyboard.row(InlineKeyboardButton(text=done_button.get(user.get('lang')),
                                      callback_data=f"add_choose_date:{year}:{month}:{day}:done"))
    keyboard.row(InlineKeyboardButton(text=back_button.get(user.get('lang')),
                                      callback_data="all_notifications"))
    return keyboard.as_markup()
