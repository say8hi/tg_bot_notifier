
choose_time_zone = {
    'ru': f"<b>Выберите ваш часовой пояс.</b>",
    'en': f"<b>Choose your time zone.</b>"
}


def personal_acc_text(user):
    return f"<b>👤Личный кабинет:</b>\n\n" \
           f"🆔Ваш ID: <code>{user.get('id')}</>\n\n" \
           f"⏲Часовой пояс: <code>{user.get('time_zone')}</>\n" \
           f"🗯Язык: <code>{user.get('lang')}</>\n" \
           f"➖➖➖➖➖➖➖➖➖" if user.get('lang') == 'ru' else \
        f"<b>Personal account:</b>\n\n" \
        f"🆔Your ID: <code>{user.get('id')}</>\n\n" \
        f"⏲Your time zone: <code>{user.get('time_zone')}</>\n" \
        f"🗯Language: <code>{user.get('lang')}</>\n" \
        f"➖➖➖➖➖➖➖➖➖"


def start_msg(full_name, lang):
    return f"<b>Приветствую,</b> <code>{full_name}</code>!" if lang == 'ru' else \
        f"<b>Welcome,</b> <code>{full_name}</code>!"
