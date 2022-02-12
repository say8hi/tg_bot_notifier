# MESSAGES
start_msg = {
    'ru': f"<b>Приветствую,</b> <code>name</code>",
    'en': f"<b>Welcome,</b> <code>name</code>"
}

notifications_menu_message = {
    'ru': f"<b>Выберите одно из ваших уведомлений для управления, либо добавьте новое уведомление.</b>",
    'en': f"<b>Choose one of your notifications to manage, or add a new notification.</b>"
}


# BUTTON TEXT
notifications_button = {
    'ru': f"🔔Ваши уведомления",
    'en': f"🔔Your notifications"
}
add_notification_button = {
    'ru': f"➕Добавить уведомление",
    'en': f"➕Add notification"
}
edit_title_button = {
    'ru': f"♻️Изменить заголовок",
    'en': f"♻️Change title"
}
edit_desc_button = {
    'ru': f"♻️Изменить описание",
    'en': f"♻️Change description"
}
edit_date_button = {
    'ru': f"♻️Изменить время",
    'en': f"♻️Change date"
}
back_button = {
    'ru': f"🔙Назад",
    'en': f"🔙Back"
}


# FUNCTIONS
def notification_desc(notification, lang):
    return f"<b>{notification.get('title')}</b>\n\n" \
           f"📜Описание: {notification.get('desc')}\n\n" \
           f"📆Придет: <code>{notification.get('date_complete')}</code>\n" \
           f"🕗Было добавлено: <code>{notification.get('date_set')}</code>\n" \
           f"➖➖➖➖➖➖➖➖➖" if lang == 'ru' else \
        f"<b>{notification.get('title')}</b>\n\n" \
           f"📜Description: {notification.get('desc')}\n\n" \
           f"📆Will notify at: <code>{notification.get('date_complete')}</code>\n" \
           f"🕗Was set on: <code>{notification.get('date_set')}</code>\n" \
           f"➖➖➖➖➖➖➖➖➖"
