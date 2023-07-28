from tg_bot.utils.db_commands import DatabaseCommands


class Database:
    users = DatabaseCommands("users")
    notifications = DatabaseCommands("notifications")
    time_zones = DatabaseCommands("time_zones")
