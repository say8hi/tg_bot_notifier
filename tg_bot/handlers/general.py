import asyncpg
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import CallbackQuery, Message

from tg_bot.filters.chats import IsPrivate
from tg_bot.keyboards.inline import main_menu, notification_menu
from tg_bot.utils.messages import start_msg, notifications_menu_message, notification_desc
from tg_bot.utils.setting_commands import set_starting_commands


async def call_main_menu(call: CallbackQuery, state: FSMContext, user: asyncpg.Record):
    await state.finish()
    await call.message.edit_text(
        start_msg.get(user.get('lang')).replace("name", call.from_user.full_name),
        reply_markup=main_menu(user.get('lang'))
    )


async def bot_start(message: Message, state: FSMContext, user: asyncpg.Record):
    await state.finish()
    await set_starting_commands(message.bot, message.from_user.id)
    await message.answer(
        start_msg.get(user.get('lang')).replace("name", message.from_user.full_name),
        reply_markup=main_menu(user.get('lang'))
    )


async def change_lang(call: CallbackQuery, user: asyncpg.Record):
    db = call.bot.get("db")
    new_lang = 'ru' if user.get('lang') == 'en' else 'en'
    await db.update_user(user.get('id'), lang=new_lang)
    await call.message.edit_text(
        start_msg.get(new_lang).replace("name", call.from_user.full_name),
        reply_markup=main_menu(new_lang)
    )


async def all_notifications(call: CallbackQuery, user: asyncpg.Record):
    await call.message.edit_text(
        notifications_menu_message.get(user.get('lang')),
        reply_markup=await notification_menu(
            call.bot.get('db'),
            user.get('id'),
            user.get('lang'))
    )


async def select_notification(call: CallbackQuery, user: asyncpg.Record):
    notif_id, db = call.data.split(":")[1], call.bot.get("db")
    notification = await db.get_notification(int(notif_id))
    await call.message.edit_text(notification_desc(notification, user.get('lang')),
                                 reply_markup=None)


def register_user(dp: Dispatcher):
    dp.register_callback_query_handler(call_main_menu, text="back_to_main_menu", state="*")
    dp.register_message_handler(bot_start, IsPrivate(), CommandStart(), state="*")
    dp.register_callback_query_handler(change_lang, text="change_lang")
    dp.register_callback_query_handler(all_notifications, text="all_notifications")
    dp.register_callback_query_handler(select_notification, text_startswith="notification:")
