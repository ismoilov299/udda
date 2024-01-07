import asyncio
import datetime
import traceback

import pandas as pd
from io import BytesIO
from aiogram.types import InputFile
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils.exceptions import MessageNotModified

from handlers.users.texts import SUM
from loader import bot, db, dp

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from states.userStates import SendUserMessageAdmin, AdminBroadcast



async def inform_admin_about_order(order_id, user_id, product_ids, latitude, longitude, amounts):
    admin_chat_id = 1161180912

    print(user_id)
    lang_id = db.get_user_language_id(user_id)

    # Fetch orders using db.get_orders_by_user_and_status
    orders = db.get_orders_by_user_and_status(user_id)  # Assuming status 1 is for processed orders
    print(orders)
    keyboard_send_message = InlineKeyboardMarkup()
    send_message_button = InlineKeyboardButton(
        "Send User Message",
        callback_data=f"send_user_{user_id}"
    )

    # Create an InlineKeyboardButton for "Deactivate"
    deactivate_button = InlineKeyboardButton(
        "Deactivate",
        callback_data=f"deactivate_{user_id}"
    )
    user = db.get_all_users(user_id)
    user_name = user[1]
    shop_name = user[6]

    # Add both buttons to the keyboard
    keyboard_send_message.add(send_message_button, deactivate_button)
    if orders:
        total_sum = 0
        # Initialize a message to send order details
        orders_message = (f"<b>Yengi buyurtmalar:</b>\n\n"
                          "<i>Buyurtmalar holati active</>\n"
                          f"Buyurtmachi: {shop_name} dan {user_name} \n\n")


        for order in orders:
            print(orders)
            # Process each order
            order_id = order['order_id']  # Correct column name for order_id
            order_status = order['status']

            # Fetch order products using db.get_order_products_by_order_id
            all_order_products = db.get_order_products_by_id(order_id)


            if all_order_products:
                for product in all_order_products:
                    # Process each product in the order
                    amount = product['amount']
                    product_name = product['name_uz']
                    formatted_amount = int(amount) if amount.is_integer() else amount
                    price = product['product_price']
                    total_price = price * amount
                    total_sum += total_price

                    # Generate the response message for each product in the order
                    product_message = (f"{formatted_amount} x {product_name}\n")
                                       # f"Soni: {amount}\n"
                                       # f"Narxi: {price} {SUM[lang_id]}\n\n")


                    # Concatenate the product details to the overall message
                    orders_message += product_message

        # Send the consolidated message with all order details
        orders_message+= f"\nJammi summa: {total_sum} {SUM[lang_id]}"
        print(orders_message)

        await bot.send_message(chat_id=admin_chat_id, text=orders_message, reply_markup=keyboard_send_message, parse_mode='html')
        await bot.send_location(chat_id=admin_chat_id,longitude=longitude,latitude=latitude)


@dp.callback_query_handler(lambda query: query.data.startswith('deactivate_'))
async def process_deactivate_callback(query: CallbackQuery, state: FSMContext):
    # Extract user_id from the callback_data
    user_id = int(query.data.split('_')[1])

    # Deactivate orders for the specified user_id
    db.deactivate_orders_by_user_id(user_id)

    # Send a response to the user
    try:
        await bot.answer_callback_query(query.id, text="Buyurtmalar o'chirildi", show_alert=True)
    except MessageNotModified:
        pass

    # Optionally, you can also update the message that triggered the callback
    await bot.edit_message_text("Buyurtma yetkaiz berildi!\n"
                                "yetkazib berilgan vaqti", query.message.chat.id, query.message.message_id)




@dp.message_handler(state=SendUserMessageAdmin.State)
async def process_admin_response(message: types.Message, state: FSMContext):
    # Extract user_id from the state
    user_id_data = await state.get_data()
    user_id = user_id_data.get('user_id')
    print(user_id)

    # Get the admin's response
    admin_response = message.text

    # Send the admin's response to the user
    await bot.send_message(user_id, f"Admindan habar {admin_response}")

    # Finish the state machine
    await state.finish()

# Modify the send_user_message_callback function
@dp.callback_query_handler(lambda query: query.data.startswith('send_user_'))
async def send_user_message_callback(query: CallbackQuery, state: FSMContext):
    # Extract user_id from callback_data
    user_id = int(query.data.split('_')[2])
    print(user_id)

    # Save user_id in the state
    await state.update_data(user_id=user_id)

    # Ask the admin for the message text
    await bot.send_message(query.from_user.id, "Habaringizni kiriting!")

    # Set the state to handle the admin's response
    await SendUserMessageAdmin.State.set()

async def check_admin(user_id: int) -> bool:
    # Implement the logic to check if the user is an admin (e.g., check against a list of admin IDs)
    admins = [1161180912, 1111111]  # Replace with actual admin IDs
    return user_id in admins

@dp.message_handler(text='All users')
async def cmd_all_users(message: types.Message):
    # Check if the user is an admin
    is_admin = await check_admin(message.from_user.id)

    if is_admin:
        # Get all users from the database
        all_users = db.get_all_users()

        # Calculate the count of users
        users_count = len(all_users)

        # Send the user count to the admin
        await message.answer(f"Userlar soni: {users_count}")
    else:
        await message.answer("Siz admin emasiz.")

async def check_admin(user_id: int) -> bool:
    # Implement the logic to check if the user is an admin (e.g., check against a list of admin IDs)
    admins = [1161180912, 987654321]  # Replace with actual admin IDs
    return user_id in admins

@dp.message_handler(text='Broadcast')
async def cmd_broadcast(message: types.Message):
    # Check if the user is an admin
    is_admin = await check_admin(message.from_user.id)

    if is_admin:
        # Prompt the admin to enter the broadcast message
        await message.answer("Barcha foydalanuvchilarga uzatmoqchi bo'lgan xabarni kiriting:")
        await AdminBroadcast.BROADCAST.set()
    else:
        await message.answer("Siz admin huquqlariga ega emasiz")


@dp.message_handler(state=AdminBroadcast.BROADCAST)
async def process_broadcast(message: types.Message, state: FSMContext):
    # Get the broadcast message from the admin
    broadcast_message = message.text

    # Get all users from the database
    all_users = db.get_all_users()

    # Send the broadcast message to all users
    for user in all_users:
        print(user)
        try:
            # Send the message to each user
            await bot.send_message(user[3], broadcast_message)
        except Exception as e:
            # Handle errors (e.g., log the error)
            print(f"Error sending broadcast message to user {user[3]}: {e}")

    # Notify the admin that the broadcast is complete
    await message.answer("Habaringiz barcha userlarga bordi!")

    # Reset the state
    await state.finish()


@dp.message_handler(commands=['day'])
async def cmd_day(message: types.Message):
    try:
        # Check if the user is an admin
        is_admin = await check_admin(message.from_user.id)

        if is_admin:
            # Check for a valid database connection
            if db:
                # Extract the date from the command arguments (e.g., "/day 2023-12-23")
                date_args = message.get_args()
                if date_args:
                    # Attempt to parse the date in a flexible manner
                    try:
                        # Parse the date in a flexible manner
                        parsed_date = datetime.datetime.strptime(date_args, '%Y-%m-%d').date()
                        # Convert the parsed date back to the string in the 'YYYY-MM-DD' format
                        date = parsed_date.strftime('%Y-%m-%d')

                        # Print the date for debugging
                        print("Date:", date)

                        # Get order product details from the database for the specified date
                        order_product_details = db.get_order_product_details(date)
                        print("Order Product Details:", order_product_details)

                        # Check if order_product_details is not empty
                        if order_product_details:
                            # Convert the result to a DataFrame using pandas
                            df = pd.DataFrame(order_product_details,
                                              columns=['amount', 'created_at', 'first_name', 'phone_number',
                                                       'shop_name', 'product_name_uz'])

                            # Create an Excel file in memory
                            excel_file = BytesIO()

                            # Use pd.ExcelWriter and specify the engine
                            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                                df.to_excel(writer, index=False, sheet_name='Order_Product_Details')

                            # Move the cursor to the beginning of the file
                            excel_file.seek(0)

                            # Save the Excel file to a specific location (e.g., within your project directory)
                            file_path = f'order_product_details_{date}.xlsx'
                            with open(file_path, 'wb') as file:
                                file.write(excel_file.read())

                            # Send a confirmation message to the admin
                            await message.answer(f"Order Product Details for {date} saved as {file_path}")
                        else:
                            await message.answer(f"No order product details found for the date: {date}")
                    except ValueError:
                        await message.answer("Noto'g'ri sana formati. Sana formati: 'YYYY-MM-DD'")
                else:
                    await message.answer("Iltimos, sanani kiritish uchun '/day YYYY-MM-DD' formatidan foydalaning.")
            else:
                await message.answer("Bot tezligi sababli, db ga ulanib bo'lmadi.")
        else:
            await message.answer("Siz admin emasiz.")
    except Exception as e:
        # Log the exception for debugging
        traceback.print_exc()

        # Respond with an error message
        await message.answer("Xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring.")


