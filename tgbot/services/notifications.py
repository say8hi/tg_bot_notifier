from datetime import datetime

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.models.db import Database


async def send_notification(bot: Bot, user_id, notification_id):
    notification = await Database.notifications.get(notification_id)
    user = await Database.users.get(user_id)
    text = f"Уведомляю вас о: <code>{notification.get('title')}</>\n\n" \
           f"Описание: {notification.get('description')}\n\n" if user.get('lang') == "ru" else \
        f"I am notifying you about: <code>{notification.get('title')}</>\n\n" \
        f"Description: {notification.get('description')}"
    await bot.send_message(user_id, text)


async def add_notification_job(notif, bot: Bot, scheduler: AsyncIOScheduler):
    date, time = notif.get('date_complete').split()
    day, month, year = date.split(".")
    hour, minute = time.split(":")
    user = await Database.users.get(notif.get("user_id"))
    scheduler.add_job(
        send_notification, "date",
        run_date=datetime(year=int(year), month=int(month), day=int(day),
                          hour=int(hour), minute=int(minute)),
        id=f"notification:{notif.get('id')}",
        args=(bot, notif.get("user_id"), notif.get('id')),
        timezone=user.get('time_zone')
    )


async def restore_notifications(bot: Bot, scheduler: AsyncIOScheduler):
    notifications = await Database.notifications.get(get_all=True)
    for notif in notifications:
        if notif.get("is_on") == 1:
            await add_notification_job(notif, bot, scheduler)
