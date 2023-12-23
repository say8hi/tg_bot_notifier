# Telegram Notifier Bot

Welcome to the Telegram Notifier Bot repository! This bot is written in Python and uses SQLite database to provide users with the ability to set their own notifications and receive alerts from the bot.

## Features

- **Custom Notifications**: You can add, modify, and delete notifications using bot commands.

- **Flexible Settings**: The bot allows you to set notifications for specific days of the week and repeat them at specified time intervals.

- **Time Zone**: You can specify your time zone to receive accurate notifications.

## Installation and Execution

1. Clone the repository to your local machine:

```bash
git clone https://github.com/say8hi/tg_bot_notifier.git
```
2. Install the necessary dependencies:
```bash
cd tg_bot_notifier
pip install -r requirements.txt
```
3. Open the **.env** file and add the environment variables:
```bash
BOT_TOKEN=your_telegram_bot_token
ADMINS=telegram_admin_id,telegram_admin_id,telegram_admin_id
```
4. Run the bot:
```bash
python bot.py
```

## Database

The bot uses SQLite database to store user notifications. You can find the database file in the main folder, after first launch, if you need to perform any additional actions with the data.
