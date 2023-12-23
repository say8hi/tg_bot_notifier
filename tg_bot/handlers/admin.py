import os

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from tg_bot.keyboards.inline import admin_menu, back_admin, choose_menu
from tg_bot.models.database import Database
from tg_bot.states.states import AdminAddTimeZone, BroadcastState
from tg_bot.utils.other_funcs import broadcast


async def admin_main(update: Message | CallbackQuery, state: FSMContext):
    await state.finish()
    if isinstance(update, CallbackQuery):
        await update.message.edit_text("Админ-меню:", reply_markup=admin_menu)
    else:
        await update.answer("Админ-меню:", reply_markup=admin_menu)


async def add_time_zone(call: CallbackQuery, state: FSMContext):
    msg_to_edit = await call.message.edit_text("Введите часовой пояс", reply_markup=back_admin)
    await AdminAddTimeZone.A1.set()
    await state.update_data(msg_to_edit=msg_to_edit)


async def add_time_zone_receive(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_to_edit = data.get("msg_to_edit")
    await message.delete()
    await Database.time_zones.add(time_zone=message.text)
    await msg_to_edit.edit_text("Готово", reply_markup=back_admin)
    await state.finish()


# Broadcast
async def broadcast_main(call: CallbackQuery, state: FSMContext):
    msg_to_edit = await call.message.edit_text("<b>Отправьте фото с текстом для рассылки\n"
                                               "|-❕Можно просто текст</b>", reply_markup=back_admin)
    await BroadcastState.BS1.set()
    await state.update_data(msg_to_edit=msg_to_edit)


async def receive_broadcast_data(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_to_edit = data.get('msg_to_edit')
    await message.delete()
    await msg_to_edit.delete()
    if message.photo:
        photo = await message.photo[-1].download(destination_dir="tg_bot")
        await state.update_data(photo=photo.name, text=message.caption)
        with open(photo.name, 'rb') as f:
            photo = f.read()
        await message.answer_photo(photo=photo, caption=f"{message.caption}\n\n"
                                                        f"<b>Все правильно? Отправляем?</b>",
                                   reply_markup=choose_menu)
    else:
        await state.update_data(text=message.text)
        await message.answer(message.text + "\n\n<b>Все правильно? Отправляем?</b>", reply_markup=choose_menu)
    await BroadcastState.next()


async def agree_and_start(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text, photo_name = data.get("text"), data.get('photo')
    await state.finish()
    await call.message.delete()
    to_delete = await call.message.answer("<b>Рассылка начата</b>")
    await broadcast(call.bot, text, photo_name)
    if photo_name:
        os.remove(photo_name)
    await to_delete.delete()
    await call.message.answer(f"<b>Рассылка закончена</b>\n", reply_markup=back_admin)


async def disagree_with_broadcast(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    photo_name = data.get('photo')
    if photo_name:
        os.remove(photo_name)
    if not call.message.photo:
        await call.message.edit_text(f"<b>Админ-меню:</b>\n"
                                     f"----------------------", reply_markup=admin_menu)
    else:
        await call.message.delete()
        await call.message.answer(f"<b>Админ-меню:</b>\n"
                                  f"----------------------", reply_markup=admin_menu)
    await state.finish()


def register_admin(dp: Dispatcher):
    # Main
    dp.register_message_handler(admin_main, commands='admin', is_admin=True)
    dp.register_callback_query_handler(admin_main, text='back_admin')

    # Add time zone
    dp.register_callback_query_handler(add_time_zone, text='add_time_zone')
    dp.register_message_handler(add_time_zone_receive, state=AdminAddTimeZone.A1)

    # Broadcast
    dp.register_callback_query_handler(broadcast_main, text="broadcast")
    dp.register_message_handler(receive_broadcast_data, content_types=['photo', 'text'], state=BroadcastState.BS1)
    dp.register_callback_query_handler(agree_and_start, text="yes", state=BroadcastState.BS2)
    dp.register_callback_query_handler(disagree_with_broadcast, text="no", state=BroadcastState.BS2)
