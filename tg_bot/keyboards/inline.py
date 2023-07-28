import calendar

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tg_bot.models.database import Database
from tg_bot.utils.messages import notifications_button, add_notification_button, back_button, edit_title_button, \
    edit_desc_button, edit_date_button, delete_notification_button, month_dict, done_button, cancel_button, \
    personal_acc, order_a_bot, change_time_zone_msg, aks_for_time_zone, on_notification, off_notification


def main_menu(lang):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=notifications_button.get(lang),
                                     callback_data="all_notifications"),
                InlineKeyboardButton(text=personal_acc.get(lang), callback_data="personal_acc")
            ],
            [
                InlineKeyboardButton(text=order_a_bot.get(lang), url="https://t.me/say8hi")
            ],
            [
                InlineKeyboardButton(text="🇺🇸➡️🇷🇺" if lang == "en" else "🇷🇺➡️🇺🇸", callback_data="change_lang")
            ]
        ]
    )


choose_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅Да", callback_data="yes"),
            InlineKeyboardButton(text="❌Нет", callback_data="no")
        ]
    ]
)


def personal_acc_menu(lang):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=change_time_zone_msg.get(lang), callback_data="change_time_zone:main")
            ],
            [
                InlineKeyboardButton(text=back_button.get(lang), callback_data="back_to_main_menu")
            ]
        ]
    )


admin_menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📬Рассылка", callback_data="broadcast")
            ],
            [
                InlineKeyboardButton(text="➕Добавить часовой пояс", callback_data="add_time_zone")
            ]
        ]
    )


back_admin = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔙Назад", callback_data="back_admin")
            ]
        ]
    )


def time_zone_menu(time_zones, user):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for record in time_zones:
        keyboard.insert(InlineKeyboardButton(
            text=f"{'✅' if user.get('time_zone') == record.get('time_zone') else ''}{record.get('time_zone')}",
            callback_data=f"change_time_zone:{record.get('time_zone')}")
        )
    keyboard.add(InlineKeyboardButton(text=aks_for_time_zone.get(user.get('lang')), url="https://t.me/say8hi"))
    keyboard.add(InlineKeyboardButton(text=back_button.get(user.get('lang')), callback_data="personal_acc"))
    return keyboard


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
    keyboard = InlineKeyboardMarkup(row_width=2)
    user_notifications = await Database.notifications.custom_sql(f"SELECT * FROM notifications WHERE user_id={user_id}")
    for notification in user_notifications:
        keyboard.insert(InlineKeyboardButton(text=notification.get("title"),
                                             callback_data=f"notification:{notification.get('id')}"))
    keyboard.add(InlineKeyboardButton(text=add_notification_button.get(lang),
                                      callback_data="add_notification"))
    keyboard.add(InlineKeyboardButton(text=back_button.get(lang),
                                      callback_data="back_to_main_menu"))
    return keyboard


async def select_date_menu(user, year, month, day):
    keyboard = InlineKeyboardMarkup(row_width=7)
    day_count = calendar.monthrange(int(year), int(month))
    keyboard.add(InlineKeyboardButton(text="⬅️", callback_data=f"add_choose_date:{year}:{int(month) - 1}:{day}:not"))
    keyboard.insert(InlineKeyboardButton(text=month_dict.get(int(month)).get(user.get('lang')), callback_data=f"..."))
    keyboard.insert(
        InlineKeyboardButton(text="➡️️", callback_data=f"add_choose_date:{year}:{int(month) + 1}:{day}:not"))
    keyboard.add(InlineKeyboardButton(text="1", callback_data=f"add_choose_date:{year}:{month}:{1}:not"))
    for i in range(2, day_count[1] + 1):
        if i == int(day):
            keyboard.insert(InlineKeyboardButton(text=f"✅{i}", callback_data=f"..."))
            continue
        keyboard.insert(InlineKeyboardButton(text=str(i), callback_data=f"add_choose_date:{year}:{month}:{i}:not"))
    keyboard.add(InlineKeyboardButton(text=done_button.get(user.get('lang')),
                                      callback_data=f"add_choose_date:{year}:{month}:{day}:done"))
    keyboard.add(InlineKeyboardButton(text=back_button.get(user.get('lang')),
                                      callback_data="all_notifications"))
    return keyboard
