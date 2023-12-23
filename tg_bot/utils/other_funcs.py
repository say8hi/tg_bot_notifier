from datetime import datetime

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tg_bot.models.database import Database


async def send_notification(bot: Bot, user_id, notification_id):
    notification = await Database.notifications.get(notification_id)
    user = await Database.users.get(user_id)
    text = f"Уведомляю о: <code>{notification.get('title')}</>\n\n" \
           f"Описание: {notification.get('desc')}\n\n" if user.get('lang') == "ru" else\
        f"I am notifying you about: <code>{notification.get('title')}</>\n\n" \
        f"Description: {notification.get('desc')}"
    await bot.send_message(user_id, text)


async def add_notification_job(notif, bot: Bot, scheduler: AsyncIOScheduler):
    date, time = notif.get('date_complete').split()
    day, month, year = date.split(".")
    hour, minute = time.split(":")
    user = await Database.users.get(notif.get("user_id"))
    scheduler.add_job(send_notification, "date", run_date=datetime(
        year=int(year), month=int(month), day=int(day), hour=int(hour), minute=int(minute)
    ),
                      id=f"notification:{notif.get('id')}", args=(bot, notif.get("user_id"), notif.get('id')),
                      timezone=user.get('time_zone')
                      )


async def restore_notifications(bot: Bot, scheduler: AsyncIOScheduler):
    notifications = await Database.notifications.get(get_all=True)
    for notif in notifications:
        if notif.get("is_on") == 1:
            await add_notification_job(notif, bot, scheduler)


async def broadcast(bot: Bot, text: str, photo: str = None):
    users = await Database.users.get(get_all=True)
    if photo:
        with open(photo, 'rb') as f:
            data = f.read()
    for user in users:
        try:
            if photo:
                await bot.send_photo(chat_id=user.get("id"), photo=data, caption=text)
            else:
                await bot.send_message(chat_id=user.get("id"), text=text)
        except Exception:
            pass
