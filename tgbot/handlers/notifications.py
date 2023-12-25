from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.filters.chat import IsPrivate
from tgbot.keyboards.inline import notification_menu, inside_notification_menu, back_to_notification_menu, \
    select_date_menu, agree_menu, back_to_notification_edit_menu, confirm_editing_notification
from tgbot.messages.reply_buttons import notifications_button
from tgbot.misc.states import AddNotificationState, EditNotificationDescTitle, EditNotificationDate
from tgbot.models.db import Database
from tgbot.messages.notifications_msg import *
from tgbot.services.notifications import add_notification_job

notifications_router = Router()
notifications_router.message.filter(IsPrivate())


@notifications_router.message(F.text.in_(notifications_button.values()))
@notifications_router.callback_query(F.data == "all_notifications")
async def all_notifications(update: Message | CallbackQuery, state: FSMContext, user: dict):
    await state.clear()
    if isinstance(update, Message):
        await update.answer(
            notifications_menu_message.get(user.get('lang')),
            reply_markup=await notification_menu(user.get('id'), user.get('lang'))
        )
        return

    await update.message.edit_text(
        notifications_menu_message.get(user.get('lang')),
        reply_markup=await notification_menu(user.get('id'), user.get('lang'))
    )


@notifications_router.callback_query(F.data.startswith('notification:'))
async def select_notification(call: CallbackQuery, user: dict):
    notif_id = int(call.data.split(":")[1])
    notification = await Database.notifications.get(notif_id)
    await call.message.edit_text(notification_desc(notification, user.get('lang')),
                                 reply_markup=inside_notification_menu(lang=user.get("lang"),
                                                                       notification_id=notif_id,
                                                                       enabled=notification.get("is_on")))


@notifications_router.callback_query(F.data.startswith('enable_notification:'))
async def enable_notification(call: CallbackQuery, user: dict, scheduler: AsyncIOScheduler):
    notification_id = int(call.data.split(":")[1])
    notification = await Database.notifications.get(notification_id)
    job = scheduler.get_job(f"notification:{notification_id}")
    if notification.get('is_on') == 1:
        await Database.notifications.update(notification_id, is_on=0)
        if job:
            job.remove()
        enabled = 0
    else:
        await Database.notifications.update(notification_id, is_on=1)
        if not job:
            await add_notification_job(notification, call.bot, scheduler)
        enabled = 1
    await call.message.edit_text(notification_desc(notification, user.get('lang')),
                                 reply_markup=inside_notification_menu(lang=user.get("lang"),
                                                                       notification_id=notification_id,
                                                                       enabled=enabled))


@notifications_router.callback_query(F.data.startswith('edit_notification:'))
async def edit_notification(call: CallbackQuery, state: FSMContext, user: dict):
    option, notif_id = call.data.split(":")[1], int(call.data.split(":")[2])
    if option == "delete":
        await Database.notifications.delete(int(notif_id))
        await call.message.edit_text(notification_deleted_message.get(user.get("lang")),
                                     reply_markup=back_to_notification_menu(user.get('lang')))
        return

    notification = await Database.notifications.get(notif_id)
    if option in ('title', 'description'):
        await state.set_state(EditNotificationDescTitle.receive_value)
        msg = await call.message.edit_text(edit_tile_desc_msg(option, notification.get(option), user.get('lang')),
                                           reply_markup=back_to_notification_edit_menu(user.get('lang'), notif_id))
        await state.update_data(msg_id=msg.message_id, notif_id=notif_id, option=option)
        return

    else:
        await call.answer("❗️This function in development right now." if user.get('lang') == 'en' else
                          "❗️Эта функция находится в разработке")


@notifications_router.message(EditNotificationDescTitle.receive_value)
async def receive_title_desc(message: Message, state: FSMContext, user: dict):
    data = await state.get_data()
    msg_id, notif_id, option, value = data.get("msg_id"), data.get('notif_id'), data.get("option"), message.text
    notif = await Database.notifications.get(notif_id)
    await message.delete()
    await message.bot.edit_message_text(edit_tile_desc_confirm(option, notif.get(option), value, user.get('lang')),
                                        chat_id=message.from_user.id, message_id=msg_id,
                                        reply_markup=confirm_editing_notification(user.get('lang'), notif_id))
    await state.set_state(EditNotificationDescTitle.confirm)
    await state.update_data(new_value=value)


@notifications_router.callback_query(F.data == 'confirm_editing_notif', EditNotificationDescTitle.confirm)
async def confirm_edit(call: CallbackQuery, state: FSMContext, user: dict):
    data = await state.get_data()
    notif_id, option, new_value = data.get('notif_id'), data.get("option"), data.get('new_value')
    notif = await Database.notifications.get(notif_id)
    await Database.notifications.update(notif_id, **{option: new_value})
    await call.message.edit_text(successfully_edited_msg(option, notif.get(option), new_value, user.get('lang')),
                                 reply_markup=back_to_notification_edit_menu(user.get('lang'), notif_id))
    await state.clear()


@notifications_router.callback_query(F.data == 'add_notification')
async def add_notification_ask_for_title(call: CallbackQuery, state: FSMContext, user: dict):
    msg = await call.message.edit_text(send_title.get(user.get("lang")),
                                       reply_markup=back_to_notification_menu(user.get('lang')))
    await state.set_state(AddNotificationState.AN1)
    await state.update_data(msg_id=msg.message_id)


@notifications_router.message(AddNotificationState.AN1)
async def add_notification_ask_for_desc(message: Message, state: FSMContext, user: dict):
    data = await state.get_data()
    msg_id, title = data.get("msg_id"), message.text
    await message.delete()
    await message.bot.edit_message_text(send_desc(title, user.get('lang')),
                                        chat_id=message.from_user.id, message_id=msg_id,
                                        reply_markup=back_to_notification_menu(user.get('lang')))
    await state.set_state(AddNotificationState.AN2)
    await state.update_data(title=title)


@notifications_router.message(AddNotificationState.AN2)
async def add_notification_ask_for_date(message: Message, state: FSMContext, user: dict):
    data = await state.get_data()
    msg_id, title, desc = data.get("msg_id"), data.get("title"), message.text
    await message.delete()
    now = datetime.now()
    await message.bot.edit_message_text(choose_date(title, desc, user.get('lang')),
                                        chat_id=message.from_user.id, message_id=msg_id,
                                        reply_markup=await select_date_menu(user, now.year, now.month, now.day))
    await state.set_state(AddNotificationState.AN3)
    await state.update_data(desc=desc)


@notifications_router.callback_query(F.data.startswith("add_choose_date:"), AddNotificationState.AN3)
async def add_notification_receive_date(call: CallbackQuery, state: FSMContext, user: dict):
    data = await state.get_data()
    title, desc = data.get("title"), data.get("desc")
    year, month, day, done = call.data.split(":")[1:]

    if done == "done":
        date = datetime(year=int(year), month=int(month), day=int(day))
        await state.set_state(AddNotificationState.AN3)
        await call.message.edit_text(
            choose_time(title, desc, date.strftime("%Y.%m.%d"), user.get('lang')),
            reply_markup=back_to_notification_menu(user.get('lang')))
        await state.update_data(date=f"{day}.{month}.{year}")
        return

    if int(month) < 0:
        month = 12
    elif int(month) > 12:
        month = 1

    date = datetime(year=int(year), month=int(month), day=int(day))
    if date < datetime.now() and date.strftime("%Y.%m.%d") != datetime.now().strftime("%Y.%m.%d"):
        await call.answer(past_date.get(user.get('lang')), show_alert=True)
        return
    await call.message.edit_text(choose_date(title, desc, user.get('lang')),
                                 reply_markup=await select_date_menu(user, year, month, day))


@notifications_router.message(AddNotificationState.AN3)
async def add_notification_receive_time(message: Message, state: FSMContext, user: dict):
    data = await state.get_data()
    msg_id, title, desc = data.get("msg_id"), data.get("title"), data.get("desc")
    date = data.get("date")
    time = message.text.split(":")
    await message.delete()
    if len(time) == 2 and time[0].isdigit() and time[1].isdigit():
        await state.set_state(AddNotificationState.AN4)
        day, month, year = date.split(".")
        date = datetime(year=int(year), month=int(month), day=int(day))
        await message.bot.edit_message_text(
            last_agree(title, desc, date.strftime("%Y.%m.%d"), ":".join(time), user.get('lang')),
            chat_id=message.from_user.id, message_id=msg_id,
            reply_markup=agree_menu(user.get('lang'))
        )
        await state.update_data(time=":".join(time))
    else:
        await message.bot.edit_message_text(wrong_format.get(user.get("lang")), chat_id=message.from_user.id)


@notifications_router.callback_query(F.data.startswith("done_adding"), AddNotificationState.AN4)
async def add_notification_done(call: CallbackQuery, state: FSMContext, user: dict, scheduler: AsyncIOScheduler):
    data = await state.get_data()
    title, desc, date, time = data.get("title"), data.get("desc"), data.get("date"), data.get("time")
    notification = await Database.notifications.add(user_id=call.from_user.id,
                                                    description=desc,
                                                    date_complete=f"{date} {time}",
                                                    date_set=datetime.now().strftime("%Y.%m.%d %H:%M"),
                                                    title=title)
    await add_notification_job(notification, call.bot, scheduler)
    await call.message.edit_text(notification_done.get(user.get('lang')),
                                 reply_markup=back_to_notification_menu(user.get('lang')))
    await state.clear()
