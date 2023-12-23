from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message


class GlobalInstances(BaseMiddleware):
    def __init__(self, config, scheduler) -> None:
        self.config = config
        self.scheduler = scheduler

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        data["config"] = self.config
        data["scheduler"] = self.scheduler
        result = await handler(event, data)
        return result
