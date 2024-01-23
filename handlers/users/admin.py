import asyncio
import sqlite3
from datetime import datetime, timedelta
import traceback
from io import BytesIO
import seaborn as sns
from faker import Faker
import random
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import openpyxl
import pandas as pd
import numpy as np
from io import BytesIO
from aiogram.types import InputFile, ParseMode
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils.exceptions import MessageNotModified

from handlers.users.texts import SUM
from loader import bot, db, dp

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from states.userStates import SendUserMessageAdmin, AdminBroadcast



async def inform_admin_about_order(user_id, order_ids, product_ids, amounts,comment):
    admin_chat_id = -1002064650084

    lang_id = db.get_user_language_id(user_id)

    # Fetch orders using db.get_orders_by_user_and_status
    orders = db.get_orders_by_user_and_status(user_id)  # Assuming status 1 is for processed orders

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
    user = db.get_user_by_chat_id(user_id)

    user_name = user[1]
    shop_name = user[6]
    user_phone = user[4]

    # Add both buttons to the keyboard
    keyboard_send_message.add( deactivate_button)

    if orders:
        total_sum = 0
        # Initialize a message to send order details
        orders_message = (f"<b>Yengi buyurtmalar:</b>\n\n"
                          "<i>Buyurtmalar holati active</>\n"
                          f"👤Buyurtmachi: {shop_name} dan {user_name}\n"
                          f"📞Buyurtmachining raqami: +{user_phone} \n\n")

        for order in orders:
            print(order)
            print(user)
            # Process each order
            order_id = order['order_id']  # Correct column name for order_id
            order_status = order['status']

            # Fetch order products using db.get_order_products_by_order_id
            all_order_products = db.get_order_products_by_id(order_id)

            if all_order_products:
                    for product in all_order_products:
                        amount = product['amount']
                        product_name = product['name_uz']
                        formatted_amount = int(amount) if amount.is_integer() else amount
                        price = product['product_price']
                        total_price = price * amount
                        total_sum += total_price

                        # Generate the response message for each product in the order
                        product_message = f"{formatted_amount} x {product_name}\n"

                        # Concatenate the product details to the overall message
                        orders_message += product_message

        # Add the total sum to the order message after processing all orders
        orders_message += f"\nJammi summa: {round(total_sum, 2)}"
        if comment != "Yo'q":
            orders_message += f"\nComment: {comment}"


        # Send the consolidated message with all order details
        await bot.send_message(chat_id=admin_chat_id, text=orders_message, reply_markup=keyboard_send_message,
                               parse_mode='html')
        # await bot.send_location(chat_id=admin_chat_id, longitude=longitude, latitude=latitude)




@dp.callback_query_handler(lambda query: query.data.startswith('deactivate_'))
async def process_deactivate_callback(query: CallbackQuery, state: FSMContext):
    # Extract user_id from the callback_data
    user_id = int(query.data.split('_')[1])

    # Deactivate orders for the specified user_id
    db.deactivate_orders_by_user_id(user_id)

    # Send a response to the user
    try:
        await bot.answer_callback_query(query.id, text="Ajoyib yana bitta buyurtmani yetkazib berdik 🎉 ", show_alert=True)
    except MessageNotModified:
        pass
    delivery_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    await query.message.delete_reply_markup()
    await query.message.reply(f'Buyurtma yetkazildi ✅ \n'
                              f'yetkazib berilgan vaqt: {delivery_time}\n'
                              f'yetkazib beruvchi {query.from_user.full_name}')
    # Optionally, you can also update the message that triggered the callback
    # await bot.edit_message_text("Buyurtma yetkazib berildi!\n"
    #                             "yetkazib berilgan vaqti", query.message.chat.id, query.message.message_id)




@dp.message_handler(state=SendUserMessageAdmin.State)
async def process_admin_response(message: types.Message, state: FSMContext):
    # Extract user_id from the state

    user_id_data = await state.get_data()
    user_id = user_id_data.get('user_id')


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


    # Save user_id in the state
    await state.update_data(user_id=user_id)

    # Ask the admin for the message text
    await bot.send_message(query.from_user.id, "Habaringizni kiriting!")

    # Set the state to handle the admin's response
    await SendUserMessageAdmin.State.set()

async def check_admin(user_id: int) -> bool:
    # Implement the logic to check if the user is an admin (e.g., check against a list of admin IDs)
    admins = [1330868035]  # Replace with actual admin IDs
    return user_id in admins

@dp.message_handler(text='All users')
async def cmd_all_users(message: types.Message):
    # Check if the user is an admin
    admin_id = message.from_user.id

    # Use get_admin_by_chat_id to check if the user is an admin
    admin_info = db.get_admin_by_chat_id(admin_id)

    if admin_info:
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
    admins = [1330868035]  # Replace with actual admin IDs
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
        await message.answer("Kechirasiz! Siz admin huquqlariga ega emasiz.Bu buyruqdan faqat admin foydalana oladi")


@dp.message_handler(state=AdminBroadcast.BROADCAST)
async def process_broadcast(message: types.Message, state: FSMContext):
    # Get the broadcast message from the admin
    broadcast_message = message.text

    # Get all users from the database
    all_users = db.get_all_users()

    # Send the broadcast message to all users
    for user in all_users:

        try:
            # Send the message to each user
            await bot.send_message(user[3], broadcast_message)
        except Exception as e:
            # Handle errors (e.g., log the error)
            print(f"Error sending broadcast message to user {user[3]}: {e}")

    # Notify the admin that the broadcast is complete
    await message.answer("Habaringiz barcha foydalanuvchilarga bordi!")

    # Reset the state
    await state.finish()

import io


@dp.message_handler(Command("xisobot"))
async def on_command_day(message: types.Message):
    is_admin = await check_admin(message.from_user.id)

    if is_admin:
        try:
            # Получение текущей даты
            today_date = datetime.now().strftime('%Y-%m-%d')

            # Подключение к базе данных SQLite
            conn = sqlite3.connect('back/db.sqlite3')
            cursor = conn.cursor()

            # Вывод SQL-запроса с алиасами таблиц и столбцов в консоль
            sql_query = f"""
                WITH OrderIds AS (
                    SELECT DISTINCT order_id
                    FROM bot_app_order
                    WHERE strftime(?, bot_app_order.created_at) = '{today_date}'
                )
                SELECT 
                    op.amount AS количество_товара,
                    op.created_at AS дата_создания_заказа,
                    bot_app_user.first_name AS имя_пользователя,
                    bot_app_user.phone_number AS номер_телефона_пользователя,
                    bot_app_user.shop_name AS название_магазина,
                    bot_app_product.name_uz AS наименование_товара,
                    bot_app_product.price AS цена_товара,
                    bot_app_product.price * op.amount AS общая_стоимость_товара
                FROM 
                    bot_app_orderproduct op
                JOIN 
                    OrderIds o ON op.id = o.order_id
                JOIN 
                    bot_app_user ON bot_app_user.chat_id = op.user_id
                JOIN 
                    bot_app_product ON bot_app_product.id = op.product_id
            """




            # Выполнение SQL-запроса с использованием текущей даты
            cursor.execute(sql_query, ('%Y-%m-%d',))

            # Получение результатов запроса
            results = cursor.fetchall()

            # Создание файла Excel
            wb = openpyxl.Workbook()
            ws = wb.active
            # headers = ["Maxsulot soni", "Sana", "Buyurtmachining ismi", "Telefon raqami",
            #            #                    "Do'kon nomi", "Maxsulot nomi", "Narxi", "Ummumiy narxi"]
            # Заголовки
            headers = ["Maxsulot soni", "Sana", "Buyurtmachining ismi", "Telefon raqami",
                       "Do'kon nomi", "Maxsulot nomi", "Narxi", "Ummumiy narxi"]
            ws.append(headers)

            # Добавление данных
            total_sales = 0  # Общая стоимость всех товаров
            for row in results:
                ws.append(row)
                total_sales += row[-1]  # Общая стоимость товара находится в последнем столбце

            # Добавление строки с общей стоимостью
            total_row = ["Ummumiy kunlik savdo", "", "", "", "", "", "", total_sales]
            ws.append(total_row)

            # Создание временного файла Excel
            excel_file = io.BytesIO()
            wb.save(excel_file)
            excel_file.seek(0)

            # Отправка файла Excel пользователю
            await message.answer_document(InputFile(excel_file, filename=f"hisobot_{today_date}.xlsx"))

        except Exception as e:
            print(e)
            await message.answer("Bazada ma'lumotlar mavjud emsa")

        finally:
            # Закрытие соединения с базой данных
            conn.close()

    else:
        await message.answer("Kechirasiz! Siz admin huquqlariga ega emasiz.Bu buyruqdan faqat admin foydalana oladi")


fake = Faker()


@dp.message_handler(commands=['test_stat'])
async def test_statistic_command(message: types.Message):
    try:
        sns.set_theme(style="darkgrid")


        fake_results = []


        for _ in range(100):
            date = fake.date_between(start_date='-7d', end_date='today')
            count = random.randint(1, 10)
            fake_results.append((date, 'M3 qisqich 1mm', count))


        for _ in range(100):
            date = fake.date_between(start_date='-7d', end_date='today')
            count = random.randint(1, 10)
            fake_results.append((date, 'Model 2 qisqich', count))


        for _ in range(50):
            date = fake.date_between(start_date='-7d', end_date='today')
            count = random.randint(1, 10)
            fake_results.append((date, 'M2 Xanjar', count))


        fake_results.extend(fake_results[-50:])

        df = pd.DataFrame(fake_results, columns=['Sana', 'Maxsulot', 'Soni'])

        plt.figure(figsize=(10, 6))
        sns.countplot(data=df, x='Sana', hue='Maxsulot', palette='Set1')

        plt.title('7 kunlik Statistka malumotlari')
        plt.xlabel('Sana')
        plt.ylabel('Maxsulot soni')


        plt.legend(title='Maxsulot')

        plt.grid(True)

        chart_file = BytesIO()
        plt.savefig(chart_file, format='png')
        chart_file.seek(0)
        plt.close()

        await message.answer_photo(chart_file)

    except Exception as e:
        print(e)
        await message.answer("Ma'lumotlarda qandaydur xatolik bor")
@dp.message_handler(commands=['groupid'])
async def get_group_id(message: types.Message):
    chat_id = message.chat.id
    await message.reply(f"Gruhning ID raqami: {chat_id}")

@dp.message_handler(commands=['id'])
async def get_group_id(message: types.Message):
    chat_id = message.from_user.id
    await message.reply(f"Sizning ID raqamingiz: {chat_id}")


@dp.message_handler(commands=['admin_commands'])
async def admin_commands(message: types.Message):
    commands_text = ("<b>Admin uchun buyruqlar</b>\n"
                     "/groupid - <i> gruhning id raqamini olish uchun</i> (buyruq vaqtinchalik)\n"
                     "/test_stat - <i> test rejimdagi 7 kunlik statistika ma'lumotlari</i> (buyruq vaqtinchalik)\n"
                     "/stats - <i> 7 kunlik statistik ma'lumotlar ni olish uchun</i>\n"
                     "/xisobot - <i> kunlik sotuvlar bo'yicha xisobot</i>\n"
                     "/id - <i> foydalanuvchini id sini tashlaydi (barcha uchun)</i>\n"
                     "/add_admin - <i> admin larni qo'shish uchun (id orqali)</i>")

    await message.answer(text=commands_text, parse_mode='html')

@dp.message_handler(commands=['stats'])
async def send_stats(message: types.Message):
    is_admin = await check_admin(message.from_user.id)

    if is_admin:

        conn = sqlite3.connect('back/db.sqlite3')
        cursor = conn.cursor()

        today_date = datetime.now().strftime('%Y-%m-%d')
        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

        query = f"""
            SELECT 
                strftime('%Y-%m-%d', op.created_at) AS Sana,
                bot_app_product.name_uz AS "Maxsulot nomi",
                CAST(SUM(op.amount) AS INTEGER) AS Soni
            FROM 
                bot_app_orderproduct op
            JOIN 
                bot_app_product ON bot_app_product.id = op.product_id
            WHERE 
                op.created_at BETWEEN '{seven_days_ago}' AND '{today_date}'
            GROUP BY Sana, "Maxsulot nomi"
        """

        cursor.execute(query)
        result = cursor.fetchall()

        try:
            import pandas as pd
            df = pd.DataFrame(result, columns=['Date', 'Product', 'Amount'])

            plt.figure(figsize=(10, 6))
            sns.barplot(x='Date', y='Amount', hue='Product', data=df, palette='Set1')
            sns.set_theme(style="darkgrid")
            plt.yticks(range(0, max(df['Amount']) + 1, 1))

            plt.xlabel('Sana')
            plt.ylabel('Sonni')
            plt.title('Oxirgi 7 kunlik mahsulot statistikasi')
            plt.legend(title='Maxsulotlar')

            plt.savefig('bar_plot.png')

            conn.close()

            photo = types.InputFile('bar_plot.png')
            await message.reply_photo(photo, caption='Oxirgi 7 kunlik mahsulot statistikasi')

        except:
            await message.answer("Kechirasiz admin hozir bazada ma'lumotlar yetarli emas")

    else:
        await message.answer("Kechirasiz! Siz admin huquqlariga ega emasiz.Bu buyruqdan faqat admin foydalana oladi")
