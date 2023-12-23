from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from tgbot.messages.reply_buttons import *


def main_menu(lang):
    return ReplyKeyboardMarkup(resize_keyboard=True,
                               keyboard=[
                                   [
                                       KeyboardButton(text=notifications_button.get(lang)),
                                       KeyboardButton(text=personal_acc.get(lang))
                                   ],
                                   [
                                       KeyboardButton(text="🇺🇸➡️🇷🇺" if lang == "en" else "🇷🇺➡️🇺🇸"),
                                   ]
                               ])
