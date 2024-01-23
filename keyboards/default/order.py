from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from handlers.users.texts import NO_CART, CART_ORDER, BTN_ORDER, BTN_MY_ORDERS, BTN_COMMENTS, BTN_ABOUT_US, \
    BTN_SETTINGS, KORZINKA, SUM, BTN_KORZINKA, AT_KORZINKA, ALL
from loader import dp, db




@dp.message_handler(text=['🗑 Savatcha', '🗑 Корзина'])
async def handle_product_request(message: types.Message):
    user_id = message.from_user.id
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




        # Check if total_sum is non-zero before sending the message
        if total_sum > 0:
            # Add the total sum to the message
            all_orders_message += f"{ALL[lang_id]} {total_sum}"
            # Send the consolidated message with all order details and total sum
            await message.answer(text=all_orders_message, reply_markup=keyboard_buy_all)
        else:
            await message.answer(text=NO_CART[lang_id])

    else:
        # If there are no orders, send a message to the user
        await message.answer(text=NO_CART[lang_id])




# get_all_about_data

@dp.message_handler(text=['👨‍👩‍👦 Biz haqimizda', '👨‍👩‍👦 O нас'])
async def handle_about(message: types.Message):
    user_id = message.from_user.id
    lang_id = db.get_user_language_id(user_id)
    about = db.get_all_about_data()

    # Corrected syntax to access 'text_uz' value

    text_uz = about[0]['text_uz']
    text_ru = about[0]['text_ru']

    if lang_id == 1:
        await message.answer(text_uz)
    else:
        await message.answer(text_ru)
