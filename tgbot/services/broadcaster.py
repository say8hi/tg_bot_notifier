import logging

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InputFile, ReplyKeyboardMarkup


async def broadcast(
        bot: Bot,
        users: list,
        text: str,
        photo: str | InputFile = None,
        disable_notification: bool = False,
        reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup = None,
) -> tuple:
    sent, not_sent = 0, 0
    try:
        for user in users:
            if not photo:
                try:
                    await bot.send_message(user.get('id'), text, disable_notification=disable_notification,
                                           reply_markup=reply_markup, disable_web_page_preview=True)
                    sent += 1
                except Exception:
                    not_sent += 1
            else:
                try:
                    await bot.send_photo(user.get('id') if isinstance(user, dict) else user, photo=photo,
                                         disable_notification=disable_notification, reply_markup=reply_markup)
                    sent += 1
                except Exception:
                    not_sent += 1
    finally:
        logging.info(f"BROADCAST: {sent} messages sent and {not_sent} not sent")

    return sent, not_sent
