from aiogram.fsm.state import StatesGroup, State


class BroadcastState(StatesGroup):
    BS1 = State()
    BS2 = State()


class GiveAccessState(StatesGroup):
    receive_value = State()
    agree = State()


class AdminAddTimeZone(StatesGroup):
    A1 = State()


class AddNotificationState(StatesGroup):
    AN1 = State()
    AN2 = State()
    AN3 = State()
    AN4 = State()
    AN5 = State()


class EditNotificationDescTitle(StatesGroup):
    receive_value = State()
    confirm = State()


class EditNotificationDate(StatesGroup):
    choose_value = State()

