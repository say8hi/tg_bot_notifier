from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tg_bot.utils.messages import notifications_button, add_notification_button, back_button


def main_menu(lang):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=notifications_button.get(lang),
                                     callback_data="all_notifications")
            ],
            [
                InlineKeyboardButton(text="🇺🇸➡️🇷🇺" if lang == "en" else "🇷🇺➡️🇺🇸", callback_data="change_lang")
            ]
        ]
    )


def inside_notification_menu(lang):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=notifications_button.get(lang),
                                     callback_data="all_notifications")
            ],
            [
                InlineKeyboardButton(text=back_button.get(lang),
                                     callback_data="back_to_main_menu")
            ]
        ]
    )


close_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✖️Закрыть", callback_data="close")
        ]
    ]
)

back_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙Назад", callback_data="back")
        ]
    ]
)


async def notification_menu(db, user_id, lang):
    keyboard = InlineKeyboardMarkup(row_width=2)
    user_notifications = await db.get_notification(user_id, get_all=True)
    for notification in user_notifications:
        keyboard.insert(InlineKeyboardButton(text=notification.get("title"),
                                             callback_data=f"notification:{notification.get('id')}"))
    keyboard.add(InlineKeyboardButton(text=add_notification_button.get(lang),
                                      callback_data="add_notification"))
    keyboard.add(InlineKeyboardButton(text=back_button.get(lang),
                                      callback_data="back_to_main_menu"))
    return keyboard
