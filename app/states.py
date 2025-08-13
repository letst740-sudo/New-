from aiogram.fsm.state import StatesGroup, State
class RegStates(StatesGroup):
    ASK_GENDER = State()
    ASK_AGE = State()
