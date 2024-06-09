from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.database.models import User
from tgbot.filters.chat import IsPrivate
from tgbot.keyboards.inline import personal_acc_menu, time_zone_menu
from tgbot.keyboards.reply import main_menu
from tgbot.database.orm import AsyncORM
from tgbot.messages.general_user import *
from tgbot.messages.reply_buttons import *

user_router = Router()
user_router.message.filter(IsPrivate())


@user_router.callback_query(F.data == "close")
async def close_message(call: CallbackQuery):
    await call.message.delete()


@user_router.message(CommandStart())
async def bot_start(message: Message, state: FSMContext, user: User):
    await state.clear()
    await message.answer(
        start_msg(message.from_user.full_name, user.lang),
        reply_markup=main_menu(user.lang),
    )


@user_router.message(F.text.in_(["🇺🇸➡️🇷🇺", "🇷🇺➡️🇺🇸"]))
async def change_lang(message: Message, user: User):
    new_lang = "ru" if user.lang == "en" else "en"
    await AsyncORM.users.update(user.id, lang=new_lang)
    user = await AsyncORM.users.get(user.id)
    await message.answer(
        start_msg(message.from_user.full_name, user.lang),
        reply_markup=main_menu(new_lang),
    )


@user_router.callback_query(F.data == "personal_acc")
@user_router.message(F.text.in_(personal_acc.values()))
async def personal_acc_handler(update: Message | CallbackQuery, user: User):
    if isinstance(update, Message):
        await update.answer(
            personal_acc_text(user), reply_markup=personal_acc_menu(user.lang)
        )
        return

    await update.message.edit_text(
        personal_acc_text(user), reply_markup=personal_acc_menu(user.lang)
    )


@user_router.callback_query(F.data.startswith("change_time_zone:"))
async def change_time_zone_handler(call: CallbackQuery, user: User):
    option = call.data.split(":")[1]
    if option != "main":
        await AsyncORM.users.update(call.from_user.id, time_zone=option)
        user = await AsyncORM.users.get(call.from_user.id)
    await call.message.edit_text(
        choose_time_zone.get(user.lang),
        reply_markup=time_zone_menu(await AsyncORM.time_zones.get(get_all=True), user),
    )
