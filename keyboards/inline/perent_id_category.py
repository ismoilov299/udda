from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from handlers.users.texts import TEXT_ORDER, BACK
from loader import dp, db

@dp.callback_query_handler(lambda callback: callback.data.startswith('category_'))
async def handle_category_callback(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang_id = db.get_user_language_id(user_id)
    parent_id = int(callback.data.split('_')[1])
    categories = db.get_categories_by_parent_id(parent_id)

    # Create an InlineKeyboardMarkup
    keyboard = InlineKeyboardMarkup()

    # Add buttons for the first two categories
    for category in categories:
        category_id, category_name, _, _, _ = category  # Extracting relevant data
        button_text = f"{category_name}"
        callback_data = f"product_{category_id}"  # Replace with the actual callback data
        button = InlineKeyboardButton(text=button_text, callback_data=callback_data)
        keyboard.add(button)

    # Add a "Back" button to navigate back
    back_button = InlineKeyboardButton(text=BACK[lang_id], callback_data="back_to_root")
    keyboard.add(back_button)

    # Send the keyboard to the user
    await callback.message.delete()
    await callback.message.answer(text=TEXT_ORDER[lang_id], reply_markup=keyboard)

@dp.callback_query_handler(lambda callback: callback.data == 'back_to_root')
async def handle_back_to_root_callback(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang_id = db.get_user_language_id(user_id)

    # Add logic to determine the appropriate action when the "Back" button is clicked
    # For example, you can go back to the previous menu or perform another action

    # Get root categories
    root_categories = db.get_root_categories()

    # Create an InlineKeyboardMarkup
    keyboard = InlineKeyboardMarkup()

    # Add buttons for the root categories
    for category in root_categories:
        category_id, category_name, _, _, _ = category  # Extracting relevant data
        button_text = f"{category_name}"
        callback_data = f"category_{category_id}"  # Replace with the actual callback data
        button = InlineKeyboardButton(text=button_text, callback_data=callback_data)
        keyboard.add(button)

    # Send the keyboard to the user
    await callback.message.edit_text(text=TEXT_ORDER[lang_id], reply_markup=keyboard)
