from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from handlers.users.texts import TEXT_ORDER
from loader import db, dp
from states.userStates import UserStates


@dp.message_handler(text=['🛠Mahsulotlar','🛠товары'],state='*')
async def handle_product_request(message: types.Message, state: FSMContext):
    # Get top-level categories
    user_id = message.from_user.id
    lang_id = db.get_user_language_id(user_id)
    top_level_categories = db.get_root_categories()

    if lang_id == 1:
        # Create a keyboard with category buttons
        keyboard_product = InlineKeyboardMarkup()
        for category in top_level_categories:
            category_name = category[1] # Replace 'name' with the actual column name
            keyboard_product.add(InlineKeyboardButton(text=category_name, callback_data=f"category_{category[0]}"))

        # Send the keyboard to the user
        await message.answer(text=TEXT_ORDER[lang_id], reply_markup=keyboard_product)
    else:
        keyboard_product = InlineKeyboardMarkup()
        for category in top_level_categories:
            category_name = category[2] # Replace 'name' with the actual column name
            keyboard_product.add(InlineKeyboardButton(text=category_name, callback_data=f"category_{category[0]}"))

        # Send the keyboard to the user
        await message.answer(text=TEXT_ORDER[lang_id], reply_markup=keyboard_product)