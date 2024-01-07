from aiogram.dispatcher.filters.state import StatesGroup, State


class UserStates(StatesGroup):
    # Define states inside the UserStates class
    IN_START = State()
    IN_LANG = State()
    IN_NAME = State()
    IN_MENU = State()
    IN_CATEGORY= State
    IN_PRODUCT = State


class BuyAllProducts(StatesGroup):
    Name = State()
    PhoneNumber = State()
    ShopName = State()
    Location = State()

class SendUserMessageAdmin(StatesGroup):
    State = State()

class FeedbackState(StatesGroup):
    WaitingForFeedback = State()

class AdminBroadcast(StatesGroup):
    BROADCAST = State()


