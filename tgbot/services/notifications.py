from datetime import datetime

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.database.orm import AsyncORM


async def send_notification(bot: Bot, user_id, notification_id):
    notification = await AsyncORM.notifications.get(notification_id)
    user = await AsyncORM.users.get(user_id)
    text = (
        f"Уведомляю вас о: <code>{notification.title}</>\n\n"
        f"Описание: {notification.description}\n\n"
        if user.lang == "ru"
        else f"I am notifying you about: <code>{notification.title}</>\n\n"
        f"Description: {notification.description}"
    )
    await bot.send_message(user_id, text)


async def add_notification_job(notif, bot: Bot, scheduler: AsyncIOScheduler):
    date, time = notif.date_completed.split()
    day, month, year = date.split(".")
    hour, minute = time.split(":")
    user = await AsyncORM.users.get(notif.user_id)
    scheduler.add_job(
        send_notification,
        "date",
        run_date=datetime(
            year=int(year),
            month=int(month),
            day=int(day),
            hour=int(hour),
            minute=int(minute),
        ),
        id=f"notification:{notif.id}",
        args=(bot, notif.user_id, notif.id),
        timezone=user.time_zone,
    )


async def restore_notifications(bot: Bot, scheduler: AsyncIOScheduler):
    notifications = await AsyncORM.notifications.get(get_all=True)
    for notif in notifications:
        if notif.get("is_on") == 1:
            await add_notification_job(notif, bot, scheduler)
