from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from tgbot.database.orm import AsyncORM


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        user = await AsyncORM.users.get(event.from_user.id)

        if not user:
            user = await AsyncORM.users.create(
                id=event.from_user.id, username=event.from_user.username
            )

        if event.from_user.username != user.username:
            await AsyncORM.users.update(user.id, username=event.from_user.username)

        data["user"] = user
        result = await handler(event, data)
        return result
