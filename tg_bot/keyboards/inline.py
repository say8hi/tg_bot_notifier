from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Notifications", callback_data="all_notifications")
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
