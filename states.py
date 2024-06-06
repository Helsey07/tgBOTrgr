from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

class StatesBot(StatesGroup):
    login_entry_for_reg = State()

    money = State()
    date = State()

    operationIdentifier = State()
    replacementAmount = State()