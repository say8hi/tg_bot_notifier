import asyncio

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.inline import choose_menu, admin_menu, back_admin
from tgbot.misc.states import BroadcastState, AdminAddTimeZone
from tgbot.database.orm import AsyncORM
from tgbot.services.broadcaster import broadcast

admin_router = Router()
admin_router.message.filter(AdminFilter())


@admin_router.callback_query(F.data == "back_admin")
@admin_router.message(Command("admin"))
async def admin_start(update: Message | CallbackQuery, state: FSMContext):
    await state.clear()
    if isinstance(update, Message):
        await update.answer("Админ-меню", reply_markup=admin_menu)
        return

    await update.message.edit_text("Админ-меню", reply_markup=admin_menu)


# ======================================================================================================================
# Broadcast
@admin_router.callback_query(F.data == "broadcast")
async def broadcast_main(call: CallbackQuery, state: FSMContext):
    msg_to_edit = await call.message.edit_text(
        "<b>Отправьте фото с текстом для рассылки\n" "└─❕Можно просто текст</b>",
        reply_markup=back_admin,
    )
    await state.set_state(BroadcastState.BS1)
    await state.update_data(msg_to_edit_id=msg_to_edit.message_id)


@admin_router.message(BroadcastState.BS1, F.content_type.in_({"text", "photo"}))
async def receive_broadcast_data(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_to_edit_id = data.get("msg_to_edit_id")
    await message.delete()
    if message.photo:
        file_id = message.photo[-1].file_id
        await state.update_data(photo=file_id, text=message.caption)
        await asyncio.sleep(2)
        await message.bot.delete_message(message.from_user.id, msg_to_edit_id)
        await message.answer_photo(
            photo=file_id,
            caption=f"{message.caption}\n\n" f"<b>Все правильно? Отправляем?</b>",
            reply_markup=choose_menu,
        )
    else:
        await state.update_data(text=message.text)
        await message.bot.edit_message_text(
            f"{message.text}\n\n<b>Все правильно? Отправляем?</b>",
            message.from_user.id,
            msg_to_edit_id,
            reply_markup=choose_menu,
        )
    await state.set_state(BroadcastState.BS2)


@admin_router.callback_query(BroadcastState.BS2, F.data == "yes")
async def agree_and_start(call: CallbackQuery, state: FSMContext, bot):
    data = await state.get_data()
    text, photo_name, silent_mode = (
        data.get("text"),
        data.get("photo"),
        data.get("silent_mode"),
    )
    await state.clear()
    await call.message.delete()
    users = await Database.users.get(get_all=True)
    to_delete = await call.message.answer("<b>Рассылка начата</b>")
    done = await broadcast(
        bot, users, text, photo_name, disable_notification=silent_mode
    )
    await to_delete.delete()
    await call.message.answer(
        f"<b>Рассылка закончена</b>\n" f"Получили сообщение: <code>{done}</>\n",
        reply_markup=back_admin,
    )


@admin_router.callback_query(F.data == "add_time_zone")
async def add_time_zone(call: CallbackQuery, state: FSMContext):
    msg = await call.message.edit_text("Введите часовой пояс", reply_markup=back_admin)
    await state.set_state(AdminAddTimeZone.A1)
    await state.update_data(msg_id=msg.message_id)


@admin_router.message(AdminAddTimeZone.A1)
async def add_time_zone_receive(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_id = data.get("msg_id")
    await message.delete()
    await Database.time_zones.add(time_zone=message.text)
    await message.bot.edit_message_text(
        "Готово",
        chat_id=message.from_user.id,
        message_id=msg_id,
        reply_markup=back_admin,
    )
    await state.clear()
