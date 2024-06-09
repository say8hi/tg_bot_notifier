notifications_menu_message = {
    "ru": f"<b>Выберите одно из ваших уведомлений для управления, либо добавьте новое уведомление.</b>",
    "en": f"<b>Choose one of your notifications to manage, or add a new notification.</b>",
}

notification_deleted_message = {
    "ru": f"<b>Уведомление было удаленно.</b>",
    "en": f"<b>Notification has been deleted.</b>",
}

wrong_format = {
    "ru": f"<b>Не верный формат сообщения, попробуйте еще раз</b>",
    "en": f"<b>Wrong message format, try again.</b>",
}

notification_done = {
    "ru": f"<b>Уведомление добавлено, вы можете настроить его во вкладке 'Мои уведомления' в главном меню.\n\n"
    f"Так же в том же разделе вы сможете включить повторение этого уведомления.</b>",
    "en": f"<b>The notification has been added, you can configure it in the 'My Notifications' tab in the main menu."
    f"\n\nAlso in the same section you can enable the repetition of this notification.</b>",
}

send_title = {
    "ru": f"<b>🔖Отправьте мне заголовок вашего уведомления\n\n"
    f"Например: День рождения Вити</b>",
    "en": f"<b>🔖Send me the title of your notification\n\n"
    f"For example: Mark's birthday</b>",
}

past_date = {
    "ru": f"<b>Вы пытаетесь выбрать уже прошедшую дату.</b>",
    "en": f"<b>You are trying to choose already past date</b>",
}


# FUNCTIONS
def notification_desc(notification, lang):
    return (
        f"<b>{notification.title}</b>\n\n"
        f"📜Описание: {notification.description}\n\n"
        f"📆Придет: <code>{notification.date_completed}</code>\n"
        f"🕗Было добавлено: <code>{notification.date_created}</code>\n"
        f"➖➖➖➖➖➖➖➖➖"
        if lang == "ru"
        else f"<b>{notification.title}</b>\n\n"
        f"📜Description: {notification.description}\n\n"
        f"📆Will notify at: <code>{notification.date_completed}</code>\n"
        f"🕗Was set on: <code>{notification.date_created}</code>\n"
        f"➖➖➖➖➖➖➖➖➖"
    )


def send_desc(title, lang):
    return (
        f"<b>🔖Заголовок: <code>{title}</>\n\n"
        f"📜Отправьте мне описание вашего уведомления\n\n"
        f"Например: Купить подарок</b>"
        if lang == "ru"
        else f"<b>🔖Title: <code>{title}</>\n\n"
        f"📜Send me the description of your notification\n\n"
        f"For example: Buy a gift</b>"
    )


def choose_date(title, desc, lang):
    return (
        f"<b>🔖Заголовок: <code>{title}</>\n\n"
        f"📜Описание: {desc}\n\n"
        f"📆Выберите дату отправки уведомления</b>"
        if lang == "ru"
        else f"<b>🔖Title: <code>{title}</>\n\n"
        f"📜Description: <code>{desc}</>\n\n"
        f"📆Select the date of sending the notification</b>"
    )


def choose_time(title, desc, date, lang):
    return (
        f"<b>🔖Заголовок: <code>{title}</>\n\n"
        f"📜Описание: {desc}\n\n"
        f"📆Дата: <code>{date}</>\n\n"
        f"🕗Введите время отправки уведомления в формате 15:15</b>"
        if lang == "ru"
        else f"<b>🔖Title: <code>{title}</>\n\n"
        f"📜Description: <code>{desc}</>\n\n"
        f"📆Date: <code>{date}</>\n\n"
        f"🕗Send me the time of sending the notification as 15:15</b>"
    )


def last_agree(title, desc, date, time, lang):
    return (
        f"<b>🔖Заголовок: <code>{title}</>\n\n"
        f"📜Описание: {desc}\n\n"
        f"📆Дата: <code>{date}</>\n\n"
        f"🕗Время: <code>{time}</>\n\n"
        f"Все верно, сохранить?</b>"
        if lang == "ru"
        else f"<b>🔖Title: <code>{title}</>\n\n"
        f"📜Description: <code>{desc}</>\n\n"
        f"📆Date: <code>{date}</>\n\n"
        f"🕗Time: <code>{time}</>\n\n"
        f"Is everything correct?</b>"
    )


def edit_tile_desc_msg(arg, value, lang):
    text_dict = {
        "title": {
            "ru": f"🔖Текущий заголовок: <code>{value}</>\n\nОтправьте мне новый заголовок",
            "en": f"🔖Current title: <code>{value}</>\n\nSend me a new title",
        },
        "description": {
            "ru": f"📜Текущее описание: <code>{value}</>\n\nОтправьте мне новое описание",
            "en": f"📜Current description: <code>{value}</>\n\nSend me a new description",
        },
    }
    return text_dict.get(arg).get(lang)


def edit_tile_desc_confirm(arg, old_value, new_value, lang):
    text_dict = {
        "title": {
            "ru": f"🔖Текущий заголовок: <code>{old_value}</>\n"
            f"🔖Новый заголовок: <code>{new_value}</>\n\n"
            f"Подтвердить изменения?",
            "en": f"🔖Current title: <code>{old_value}</>\n"
            f"🔖New title: <code>{new_value}</>\n\n"
            f"Confirm editing notification?",
        },
        "description": {
            "ru": f"📜Текущее описание: <code>{old_value}</>\n"
            f"📜Новое описание: <code>{new_value}</>\n\n"
            f"Подтвердить изменения?",
            "en": f"📜Current description: <code>{old_value}</>\n"
            f"📜New description: <code>{new_value}</>\n\n"
            f"Confirm editing notification?",
        },
    }
    return text_dict.get(arg).get(lang)


def successfully_edited_msg(arg, old_value, new_value, lang):
    text_dict = {
        "title": {
            "ru": f"🔖Старый заголовок: <code>{old_value}</>\n"
            f"🔖Текущий заголовок: <code>{new_value}</>",
            "en": f"🔖Old title: <code>{old_value}</>\n"
            f"🔖Current title: <code>{new_value}</>",
        },
        "description": {
            "ru": f"📜Старое описание: <code>{old_value}</>\n"
            f"📜Текущее описание: <code>{new_value}</>",
            "en": f"📜Old description: <code>{old_value}</>\n"
            f"📜Current description: <code>{new_value}</>",
        },
        "success": {
            "ru": "✅Уведомление успешно изменено\n\n",
            "en": "✅Successfully edited notification\n\n",
        },
    }
    return text_dict.get("success").get(lang) + text_dict.get(arg).get(lang)
