from tgbot.services.db_commands import DatabaseCommands


class Database:

    users = DatabaseCommands("users")
    notifications = DatabaseCommands("notifications")
    time_zones = DatabaseCommands("time_zones")
