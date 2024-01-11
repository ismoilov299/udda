# get_products_by_category_id
import os
from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from handlers.users.texts import TEXT_PRODUCT_PRICE, TEXT_PRODUCT_DESC, TEXT_MAIN_MENU, BTN_ORDER, BTN_MY_ORDERS, \
    BTN_COMMENTS, BTN_SETTINGS, BTN_ABOUT_US, KORZINKA, BACK, BUY, CART, ALL, ORDER_NUMBER, SUM, TEXT_ORDER, \
    BTN_KORZINKA, AT_KORZINKA, NO_CART
from loader import db, dp, bot


@dp.callback_query_handler(lambda callback: callback.data.startswith('product_'))
async def handle_product_callback(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang_id = db.get_user_language_id(user_id)

    product_id = int(callback.data.split('_')[1])

    # Get product details based on the product_id
    products = db.get_products_by_category_id(product_id)
    keyboard = InlineKeyboardMarkup()

    for product in products:
        product_name = product[1] if lang_id == 1 else product[2]
        callback_data = f"pro_{product[0]}"
        button = InlineKeyboardButton(text=product_name, callback_data=callback_data)
        keyboard.add(button)

    # Add a "Back" button at the end of the keyboard
    back_button = InlineKeyboardButton(text=BACK[lang_id], callback_data="category_1")
    keyboard.add(back_button)

    await callback.message.edit_reply_markup(reply_markup=keyboard)

@dp.callback_query_handler(lambda callback: callback.data.startswith('pro_'))
async def handle_product_callback(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang_id = db.get_user_language_id(user_id)
    product_id = int(callback.data.split('_')[1])
    num = 1
    price_keyboard1 = InlineKeyboardMarkup(row_width=3)
    price_keyboard1.add(
        InlineKeyboardButton('-', callback_data=f'minus_{product_id}_{num}'),
        InlineKeyboardButton(str(num), callback_data='num'),
        InlineKeyboardButton('+', callback_data=f'plus_{product_id}_{num}'),
        InlineKeyboardButton(BUY[lang_id], callback_data=f'buy_{product_id}_{num}')
    )
    back_button = InlineKeyboardButton(text=BACK[lang_id], callback_data="category_1")
    price_keyboard1.add(back_button)

    product = db.get_product_by_id(product_id)
    print(product, ' product info')

    # Choose the appropriate column for product name based on language
    product_name = product[1] if lang_id == 1 else product[2]
    product_description = product[4] if lang_id == 1 else product[5]
    product_price = product[7]
    product_image_path = product[10]
    print(product_price)

    message_text = (f"{product_name}\n"
                    f"{TEXT_PRODUCT_DESC[lang_id]} {product_description}\n"
                    f"{TEXT_PRODUCT_PRICE[lang_id]} {product_price} ")

    if product_image_path:
        # Construct the absolute file path
        image_file_path = os.path.join(os.getcwd(), 'back/media', product_image_path)

        # Check if the image file exists
        if os.path.isfile(image_file_path):
            with open(image_file_path, 'rb') as photo:
                # Send the product with image
                await callback.message.delete()
                await bot.send_photo(chat_id=user_id, photo=photo, caption=message_text,
                                     reply_markup=price_keyboard1)
        else:
            # Log an error or handle it as needed
            print(f"File not found: {image_file_path}")
            # Send the product without image
            # await callback.message.delete()
            await callback.message.edit_text(message_text, reply_markup=price_keyboard1)
    else:
        # Send the product without image
        # await callback.message.delete()
        await callback.message.edit_text(message_text, reply_markup=price_keyboard1)

@dp.callback_query_handler(lambda callback: callback.data.startswith('plus_'))
async def on_plus_button_clicked(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang_id = db.get_user_language_id(user_id)
    _, product_id, num = callback.data.split('_')
    product_id = int(product_id)
    num = int(num)

    num += 1

    product = db.get_product_by_id(product_id)

    new_keyboard = InlineKeyboardMarkup(row_width=3)
    new_keyboard.add(
        InlineKeyboardButton('-', callback_data=f'minus_{product_id}_{num}'),
        InlineKeyboardButton(str(num), callback_data='num'),
        InlineKeyboardButton('+', callback_data=f'plus_{product_id}_{num}'),
        InlineKeyboardButton(BUY[lang_id], callback_data=f'buy_{product_id}_{num}')
    )
    await callback.answer(f"{num}")

    await callback.message.edit_reply_markup(new_keyboard)

@dp.callback_query_handler(lambda callback: callback.data.startswith('minus_'))
async def on_minus_button_clicked(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang_id = db.get_user_language_id(user_id)
    _, product_id, num = callback.data.split('_')
    product_id = int(product_id)
    num = int(num)

    num = max(1, num - 1)  # Ensure num is at least 1

    product = db.get_product_by_id(product_id)

    new_keyboard = InlineKeyboardMarkup(row_width=3)
    new_keyboard.add(
        InlineKeyboardButton('-', callback_data=f'minus_{product_id}_{num}'),
        InlineKeyboardButton(str(num), callback_data='num'),
        InlineKeyboardButton('+', callback_data=f'plus_{product_id}_{num}'),
        InlineKeyboardButton(BUY[lang_id], callback_data=f'buy_{product_id}_{num}')
    )
    await callback.answer(f"{num}")

    await callback.message.edit_reply_markup(new_keyboard)









@dp.callback_query_handler(lambda callback: callback.data.startswith('buy_'))
async def on_buy_button_clicked(callback: CallbackQuery, state: FSMContext):
    _, product_id, num = callback.data.split('_')
    product_id = int(product_id)
    num = int(num)
    user_id = callback.from_user.id

    # Replace the following line with the call to add_order_product
    db.add_order_product(product_id=product_id, amount=num, user_id=user_id)

    lang_id = db.get_user_language_id(user_id)
    product = db.get_product_by_id(product_id)
    print(product)
    price = product[7]
    total_price = round(product[7] * num, 2)
    if lang_id == 1:
        name = product[1]
    else:
        name = product[2]



    # await callback.message.delete_reply_markup()
    message_text = (f"{CART[lang_id]}\n\n"
                    f"{name}\n\n"
                    f"{TEXT_PRODUCT_PRICE[lang_id]} {price} {SUM[lang_id]}\n\n"
                    f"{ORDER_NUMBER[lang_id]} {num}\n\n"
                    f"{ALL[lang_id]} {total_price} "
                    f"")

    # Send the message with the main menu keyboard
    await callback.message.delete()
    # await callback.message.answer(message_text)
    user_id = callback.from_user.id
    lang_id = db.get_user_language_id(user_id)
    top_level_categories = db.get_root_categories()
    print(top_level_categories)
    if lang_id == 1:
        # Create a keyboard with category buttons
        keyboard_product = InlineKeyboardMarkup()
        for category in top_level_categories:
            category_name = category[1]  # Replace 'name' with the actual column name
            keyboard_product.add(InlineKeyboardButton(text='Haridni davom etirish', callback_data=f"category_{category[0]}"))

        # Send the keyboard to the user
        keyboard_product.add(InlineKeyboardButton(text='🗑 Savatcha', callback_data='show_cart'))
        await callback.message.answer(text=message_text, reply_markup=keyboard_product)
    else:
        keyboard_product = InlineKeyboardMarkup()
        for category in top_level_categories:
            category_name = category[2]  # Replace 'name' with the actual column name
            keyboard_product.add(InlineKeyboardButton(text=category_name, callback_data=f"category_{category[0]}"))

        # Send the keyboard to the user
        await callback.message.answer(text=message_text, reply_markup=keyboard_product)
    # await bot.send_message(chat_id=user_id, text=message_text)



@dp.callback_query_handler(text='show_cart')
async def show_cart(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang_id = db.get_user_language_id(user_id)

    # Get all order products for the user
    orders = db.get_all_order_products(user_id)
    # Create an InlineKeyboardMarkup
    keyboard_buy_all = InlineKeyboardMarkup()

    # Create an InlineKeyboardButton
    buy_all_button = InlineKeyboardButton(f'{BTN_KORZINKA[lang_id]}', callback_data="order_product")

    # Add the button to the keyboard
    keyboard_buy_all.add(buy_all_button)

    if orders:
        # Initialize variables for total sum calculation
        total_sum = 0
        all_orders_message = f"{AT_KORZINKA[lang_id]}\n"

        for order in orders:
            order_id = order['id']

            # Check if an order with the same order_id already exists
            existing_order = db.get_orders_by_order_id(order_id)
            if existing_order:
                print(f"Order with ID {order_id} already exists. Skipping...")
                continue

            # Process each order
            amount = order['amount']
            # Remove ".0" if the amount is a whole number
            formatted_amount = int(amount) if amount.is_integer() else amount
            product_name = order['product_name_uz']
            price = order['product_price']

            # Calculate the total price for the current order
            total_price = round(price * amount, 2)

            # Accumulate the total sum
            total_sum += total_price

            # Generate the response message for each order
            order_message = (
                f"{formatted_amount} x {product_name}\n")
            # f"Soni: {formatted_amount}\n"
            # f"Narxi: {price} {SUM[lang_id]}\n\n")

            # Concatenate the order details to the overall message
            all_orders_message += order_message

            # Print the order information for debugging
            print(order)

        # Check if total_sum is non-zero before sending the message
        if total_sum > 0:
            # Add the total sum to the message
            all_orders_message += f"Jami summa barchasi uchun: {total_sum} {SUM[lang_id]}"
            # Send the consolidated message with all order details and total sum
            await callback.message.edit_text(text=all_orders_message, reply_markup=keyboard_buy_all)
        else:
            await callback.answer(text=NO_CART[lang_id])

    else:
        # If there are no orders, send a message to the user
        await callback.answer(text=NO_CART[lang_id])





