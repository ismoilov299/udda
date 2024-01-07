from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import ReplyKeyboardRemove

from handlers.users import texts
from handlers.users.texts import BTN_ORDER, BTN_MY_ORDERS, BTN_COMMENTS, BTN_ABOUT_US, BTN_SETTINGS, TEXT_MAIN_MENU, \
    KORZINKA
from loader import dp, db
from states.userStates import UserStates
from keyboards.default import start_menu



@dp.message_handler(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    # Get user information
    user_id = message.from_user.id

    # Check if the user exists in the database
    user_exists = db.get_user_by_chat_id(user_id)

    if not user_exists:
        # If the user doesn't exist, add them to the database
        db.add_user(chat_id=user_id)

        # Set the state to IN_LANG and prompt the user to choose a language
        await UserStates.IN_LANG.set()

        keyboard_lang = types.ReplyKeyboardMarkup(resize_keyboard=True)
        lang_buttons = [texts.BTN_LANG_UZ, texts.BTN_LANG_RU]
        keyboard_lang.add(*lang_buttons)

        await message.answer(texts.WELCOME_TEXT)
        await message.answer(texts.CHOOSE_LANG, reply_markup=keyboard_lang)
    else:
        # If the user exists, set the state to IN_MENU
        await UserStates.IN_MENU.set()

        user_id = message.from_user.id
        lang_id = db.get_user_language_id(user_id)

        # Continue with your conversation flow for existing users
        keyboard_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)

        # Add the first button separately
        keyboard_menu.add(BTN_ORDER[lang_id])

        # Add the remaining buttons in pairs
        buttons_menu_row1 = [BTN_MY_ORDERS[lang_id], BTN_ABOUT_US[lang_id]]
        buttons_menu_row2 = [BTN_COMMENTS[lang_id], BTN_SETTINGS[lang_id], KORZINKA[lang_id]]

        keyboard_menu.add(*buttons_menu_row1)
        keyboard_menu.add(*buttons_menu_row2)

        # Check if the user is an admin (you need to implement this check)
        is_admin = await check_admin(user_id)

        if is_admin:
            # Add admin-specific buttons
            admin_buttons_row = ['All users', 'Broadcast']
            keyboard_menu.add(*admin_buttons_row)

        await message.answer(text=TEXT_MAIN_MENU[lang_id], reply_markup=keyboard_menu)
        await state.finish()

async def check_admin(user_id: int) -> bool:
    # Implement the logic to check if the user is an admin (e.g., check against a list of admin IDs)
    admins = [1161180912, 1111111]  # Replace with actual admin IDs
    return user_id in admins





