from datetime import datetime

import asyncpg
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tg_bot.keyboards.inline import notification_menu, inside_notification_menu, back_to_notification_menu, \
    select_date_menu, agree_menu
from tg_bot.states.states import AddNotificationState
from tg_bot.utils.messages import notifications_menu_message, notification_desc, notification_deleted_message, \
    send_title, send_desc, choose_date, choose_time, last_agree, wrong_format, notification_done
from tg_bot.utils.other_funcs import send_notification, add_notification_job


async def all_notifications(call: CallbackQuery, state: FSMContext, user: asyncpg.Record):
    await state.finish()
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
                                 reply_markup=inside_notification_menu(lang=user.get("lang"),
                                                                       notification_id=notif_id,
                                                                       enabled=notification.get("is_on")))


async def enable_notification(call: CallbackQuery, user: asyncpg.Record):
    notification_id, db = int(call.data.split(":")[1]), call.bot.get("db")
    notification = await db.get_notification(int(notification_id))
    scheduler: AsyncIOScheduler = call.bot.get("scheduler")
    job = scheduler.get_job(f"notification:{notification_id}")
    if notification.get('is_on') == 1:
        await db.update_notification(notification_id, is_on=0)
        if job:
            job.remove()
        enabled = 0
    else:
        await db.update_notification(notification_id, is_on=1)
        if not job:
            await add_notification_job(notification, db, call.bot, scheduler)
        enabled = 1
    await call.message.edit_text(notification_desc(notification, user.get('lang')),
                                 reply_markup=inside_notification_menu(lang=user.get("lang"),
                                                                       notification_id=notification_id,
                                                                       enabled=enabled))


async def edit_notification(call: CallbackQuery, state: FSMContext, user: asyncpg.Record):
    option, notif_id, db = call.data.split(":")[1], call.data.split(":")[2], call.bot.get("db")
    # notification = await db.get_notification(int(notif_id))
    if option == "delete":
        await db.del_notification(int(notif_id))
        await call.message.edit_text(notification_deleted_message.get(user.get("lang")),
                                     reply_markup=back_to_notification_menu(user.get('lang')))

    else:
        await call.answer("❗️This function in development right now." if user.get('lang') == 'en' else
                          "❗️Эта функция находится в разработке")


async def add_notification_ask_for_title(call: CallbackQuery, state: FSMContext, user: asyncpg.Record):
    msg_to_edit = await call.message.edit_text(send_title.get(user.get("lang")),
                                               reply_markup=back_to_notification_menu(user.get('lang')))
    await AddNotificationState.AN1.set()
    await state.update_data(msg_to_edit=msg_to_edit)


async def add_notification_ask_for_desc(message: Message, state: FSMContext, user: asyncpg.Record):
    data = await state.get_data()
    msg_to_edit, title = data.get("msg_to_edit"), message.text
    await message.delete()
    await msg_to_edit.edit_text(send_desc.get(user.get("lang")).replace("title", title),
                                reply_markup=back_to_notification_menu(user.get('lang')))
    await AddNotificationState.next()
    await state.update_data(title=title)


async def add_notification_ask_for_date(message: Message, state: FSMContext, user: asyncpg.Record):
    data = await state.get_data()
    msg_to_edit, title, desc = data.get("msg_to_edit"), data.get("title"), message.text
    await message.delete()
    now = datetime.now()
    await msg_to_edit.edit_text(choose_date.get(user.get("lang")).replace("title", title).replace("desc", desc),
                                reply_markup=await select_date_menu(user, now.year, now.month, now.day))
    await AddNotificationState.next()
    await state.update_data(desc=desc)


async def add_notification_receive_date(call: CallbackQuery, state: FSMContext, user: asyncpg.Record):
    data = await state.get_data()
    msg_to_edit, title, desc = data.get("msg_to_edit"), data.get("title"), data.get("desc")
    year, month, day, done = call.data.split(":")[1:]
    if done == "done":
        await AddNotificationState.next()
        date = datetime(year=int(year), month=int(month), day=int(day))
        await call.message.edit_text(
            choose_time.get(user.get('lang')).replace(
                "title", title).replace("desc", desc).replace("date", date.strftime("%Y.%m.%d")),
            reply_markup=back_to_notification_menu(user.get('lang')))
        await state.update_data(date=f"{day}.{month}.{year}")
    else:
        if int(month) < 0:
            month = 12
        elif int(month) > 12:
            month = 1
        await msg_to_edit.edit_text(choose_date.get(user.get("lang")).replace("title", title).replace("desc", desc),
                                    reply_markup=await select_date_menu(user, year, month, day))


async def add_notification_receive_time(message: Message, state: FSMContext, user: asyncpg.Record):
    data = await state.get_data()
    msg_to_edit, title, desc = data.get("msg_to_edit"), data.get("title"), data.get("desc")
    date = data.get("date")
    time = message.text.split(":")
    await message.delete()
    if len(time) == 2 and time[0].isdigit() and time[1].isdigit():
        await AddNotificationState.next()
        day, month, year = date.split(".")
        date = datetime(year=int(year), month=int(month), day=int(day))
        await msg_to_edit.edit_text(
            last_agree.get(user.get('lang')).replace(
                "title", title).replace("desc", desc).replace(
                "date", date.strftime("%Y.%m.%d")).replace("time", ":".join(time)),
            reply_markup=agree_menu(user.get('lang')))
        await state.update_data(time=":".join(time))
    else:
        await msg_to_edit.edit_text(wrong_format.get(user.get("lang")))


async def add_notification_done(call: CallbackQuery, state: FSMContext, user: asyncpg.Record):
    data = await state.get_data()
    title, desc, date, time = data.get("title"), data.get("desc"), data.get("date"), data.get("time")
    db, scheduler = call.bot.get("db"), call.bot.get("scheduler")
    day, month, year = date.split(".")
    hour, minute = time.split(":")
    notification = await db.add_notification(user_id=call.from_user.id,
                                             desc=desc,
                                             date_complete=f"{date} {time}",
                                             title=title)
    scheduler.add_job(send_notification, "date", run_date=datetime(
        year=int(year), month=int(month), day=int(day), hour=int(hour), minute=int(minute)
    ), args=(call.bot, call.from_user.id, notification.get('id')),
                      id=f"notification:{notification.get('id')}", timezone=user.get('time_zone'))
    await call.message.edit_text(notification_done.get(user.get('lang')),
                                 reply_markup=back_to_notification_menu(user.get('lang')))


def register_notifications(dp: Dispatcher):
    # Main
    dp.register_callback_query_handler(all_notifications, text="all_notifications", state="*")

    # Select and edit
    dp.register_callback_query_handler(select_notification, text_startswith="notification:")
    dp.register_callback_query_handler(edit_notification, text_startswith="edit_notification:")
    dp.register_callback_query_handler(enable_notification, text_startswith="enable_notification:")

    # Add
    dp.register_callback_query_handler(add_notification_ask_for_title, text="add_notification")
    dp.register_message_handler(add_notification_ask_for_desc, state=AddNotificationState.AN1)
    dp.register_message_handler(add_notification_ask_for_date, state=AddNotificationState.AN2)
    dp.register_callback_query_handler(add_notification_receive_date, text_startswith="add_choose_date:",
                                       state=AddNotificationState.AN3)
    dp.register_message_handler(add_notification_receive_time, state=AddNotificationState.AN4)
    dp.register_callback_query_handler(add_notification_done, text_startswith="done_adding",
                                       state=AddNotificationState.AN5)
