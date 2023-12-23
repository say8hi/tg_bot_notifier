from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.filters.chat import IsPrivate
from tgbot.keyboards.inline import personal_acc_menu, time_zone_menu
from tgbot.keyboards.reply import main_menu
from tgbot.models.db import Database
from tgbot.messages.general_user import *
from tgbot.messages.reply_buttons import *

user_router = Router()
user_router.message.filter(IsPrivate())


@user_router.callback_query(F.data == "close")
async def close_message(call: CallbackQuery):
    await call.message.delete()


@user_router.message(CommandStart())
async def bot_start(message: Message, state: FSMContext, user: dict):
    await state.clear()
    await message.answer(
        start_msg(message.from_user.full_name, user.get('lang')),
        reply_markup=main_menu(user.get('lang'))
    )


@user_router.message(F.text.in_(["🇺🇸➡️🇷🇺", "🇷🇺➡️🇺🇸"]))
async def change_lang(message: Message, user: dict):
    new_lang = 'ru' if user.get('lang') == 'en' else 'en'
    await Database.users.update(user.get('id'), lang=new_lang)
    user = await Database.users.get(user.get('id'))
    await message.answer(
        start_msg(message.from_user.full_name, user.get('lang')),
        reply_markup=main_menu(new_lang)
    )


@user_router.callback_query(F.data == "personal_acc")
@user_router.message(F.text.in_(personal_acc.values()))
async def personal_acc_handler(update: Message | CallbackQuery, user: dict):
    if isinstance(update, Message):
        await update.answer(personal_acc_text(user), reply_markup=personal_acc_menu(user.get('lang')))
        return

    await update.message.edit_text(personal_acc_text(user), reply_markup=personal_acc_menu(user.get('lang')))


@user_router.callback_query(F.data.startswith('change_time_zone:'))
async def change_time_zone_handler(call: CallbackQuery, user: dict):
    option = call.data.split(":")[1]
    if option != "main":
        await Database.users.update(call.from_user.id, time_zone=option)
        user = await Database.users.get(call.from_user.id)
    await call.message.edit_text(choose_time_zone.get(user.get('lang')),
                                 reply_markup=time_zone_menu(await Database.time_zones.get(get_all=True), user)
                                 )
