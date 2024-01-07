from aiogram import types
from aiogram.dispatcher import FSMContext

from handlers.users import texts
from handlers.users.texts import CHOOSE_LANG, BTN_ORDER, BTN_MY_ORDERS, BTN_COMMENTS, BTN_ABOUT_US, BTN_SETTINGS, \
    KORZINKA
from loader import dp, db


@dp.message_handler(text=['⚙ Sozlamalar', '⚙ Настройки'])
async def cmd_start(message: types.Message, state: FSMContext):
    # Get user information
    user_id = message.from_user.id
    keyboard_lang = types.ReplyKeyboardMarkup(resize_keyboard=True)
    lang_buttons = [texts.BTN_LANG_UZ, texts.BTN_LANG_RU]
    keyboard_lang.add(*lang_buttons)

    await message.answer(CHOOSE_LANG, reply_markup=keyboard_lang)


@dp.message_handler(lambda message: message.text in [texts.BTN_LANG_UZ, texts.BTN_LANG_RU])
async def handle_language_selection(message: types.Message, state: FSMContext):
    user_language = message.text

    # Map language to numeric value
    language_id = 1 if user_language == texts.BTN_LANG_UZ else 2

    # Save the user's language in the state
    # await state.update_data(language=language_id)
    user_id = message.from_user.id
    db.update_user_field(user_id, "lang_id", language_id)
    keyboard_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    user_id = message.from_user.id
    lang_id = db.get_user_language_id(user_id)
    # if lang_id in texts["BTN_ORDER"]:
    keyboard_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)

    # Add the first button separately
    keyboard_menu.add(BTN_ORDER[lang_id])

    # Add the remaining buttons in pairs
    buttons_menu_row1 = [BTN_MY_ORDERS[lang_id], BTN_ABOUT_US[lang_id]]
    buttons_menu_row2 = [BTN_COMMENTS[lang_id], BTN_SETTINGS[lang_id], KORZINKA[lang_id]]

    keyboard_menu.add(*buttons_menu_row1)
    keyboard_menu.add(*buttons_menu_row2)


    # You can customize the response based on the selected language
    if language_id == 1:
        await message.answer("Siz O'zbek tilini tanladingiz.",reply_markup=keyboard_menu)
    elif language_id == 2:
        await message.answer("Вы выбрали русский язык.",reply_markup=keyboard_menu)