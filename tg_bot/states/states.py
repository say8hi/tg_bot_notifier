from aiogram.dispatcher.filters.state import StatesGroup, State


class AdminAddTimeZone(StatesGroup):
    A1 = State()


class AddNotificationState(StatesGroup):
    AN1 = State()
    AN2 = State()
    AN3 = State()
    AN4 = State()
    AN5 = State()


class BroadcastState(StatesGroup):
    BS1 = State()
    BS2 = State()


class SecretState(StatesGroup):
    S1 = State()
