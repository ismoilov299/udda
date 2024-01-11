import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from handlers.users.admin import inform_admin_about_order
from handlers.users.texts import BTN_ORDER, BTN_MY_ORDERS, BTN_COMMENTS, BTN_SETTINGS, BTN_ABOUT_US, KORZINKA
from loader import dp, db, bot
from states.userStates import BuyAllProducts

@dp.callback_query_handler(lambda query: query.data == 'order_product', state='*')
async def buy_all_products_callback(query: CallbackQuery, state: FSMContext):
    user_id = query.from_user.id

    # Check if the user is already in the database
    existing_user = db.get_user_by_chat_id(user_id)
    if existing_user:
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_location = types.KeyboardButton(text="Lokatsiya yuborish", request_location=True)
        keyboard.add(button_location)

        if existing_user[1] and existing_user[4]:
            # If both name, phone number, and shop name are in the database, ask for location
            await query.message.delete()
            await query.message.answer("Buyurtma berish uchun locatsiya tashlang ", reply_markup=keyboard)

            # Check if the user is already in the 'Location' state
            current_state = await state.get_state()
            if current_state != 'BuyAllProducts:Location':
                await BuyAllProducts.Location.set()
            return
        else:
            # If not in the 'ShopName' state, set the 'ShopName' state and dynamically generate the inline keyboard for shop names
            current_state = await state.get_state()
            if current_state != 'BuyAllProducts:ShopName':
                await BuyAllProducts.ShopName.set()

                if not existing_user[1]:
                    # If the name is not present, go to the 'BuyAllProducts.Name' state
                    await BuyAllProducts.Name.set()
                    await query.message.answer("Buyurtma qilish uchun ismingizni kiritning!")

                else:
                    # Generate the inline keyboard for shop names
                    shop_names = db.get_shop_name()  # Assuming this function returns a list of tuples (shop_id, shop_name)
                    keyboard = types.InlineKeyboardMarkup()
                    for shop_id, shop_name, _ in shop_names:
                        button_shop = types.InlineKeyboardButton(text=shop_name, callback_data=f'shop_{shop_id}')
                        keyboard.add(button_shop)

                    await query.message.answer("Do'koningizning ismini tanlang", reply_markup=keyboard)
                    await BuyAllProducts.ShopName.set()

@dp.callback_query_handler(lambda query: query.data.startswith('shop_'), state=BuyAllProducts.ShopName)
async def process_shop_selection(query: CallbackQuery, state: FSMContext):
    try:
        # Extract shop_id from the callback_data
        user_id = query.from_user.id
        shop_id = int(query.data.split('_')[1])
        print(shop_id)
        existing_user = db.get_user_by_chat_id(user_id)
        print(existing_user)
        # Retrieve shop names with the given shop_id from the database
        shop_names = db.get_shop_name_parent_id(shop_id)  # Assuming this function returns a list of tuples (shop_id, shop_name)
        if existing_user[6] is None:
            if shop_names:
                keyboard = types.InlineKeyboardMarkup()
                for shop_id, shop_name, _ in shop_names:
                    button_shop = types.InlineKeyboardButton(text=shop_name, callback_data=f'shop_{shop_id}')
                    keyboard.add(button_shop)
                await query.message.delete()
                await query.message.answer("Do'koningizning ismini tanlang", reply_markup=keyboard)
            else:
                # If shop_names is empty, fetch hierarchy using get_shop_hierarchy_by_id
                shop_hierarchy = db.get_shop_hierarchy_by_id(shop_id)
                if isinstance(shop_hierarchy, dict):  # Check if shop_hierarchy is a dictionary
                    print(shop_hierarchy)
                    try:
                        shop_name = (
                            shop_hierarchy['great_grandparent_name_uz'],
                            shop_hierarchy['grandparent_name_uz'],
                            shop_hierarchy['parent_name_uz'],
                            shop_hierarchy['name_uz']
                        )

                        # Convert to a string and remove special characters
                        shop_name_str = ', '.join(map(str, shop_name))
                        shop_name_str = shop_name_str.replace("(", "").replace(")", "").replace("'", "")

                        result_message = (
                            f"Sizning do'koningiz {shop_hierarchy.get('great_grandparent_name_uz', '')} binoda "
                            f"{shop_hierarchy.get('grandparent_name_uz', '')}ning {shop_hierarchy.get('parent_name_uz', '')}da {shop_hierarchy.get('name_uz', '')}"
                        )

                        print(shop_name_str, 'shop name')
                        db.update_user_field(chat_id=user_id, key='shop_name', value=shop_name_str)
                        await query.message.answer(result_message)
                        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                        button_location = types.KeyboardButton(text="Lokatsiyangizni yuboring", request_location=True)
                        keyboard.add(button_location)
                        await query.message.answer("Lokatsiya yuboring", reply_markup=keyboard)

                        # Move to the next state 'Location'
                        await BuyAllProducts.Location.set()
                    except KeyError as e:
                        await query.message.answer(f"Xatolik: {e}.")
                else:
                    await query.message.answer("ma'lumot topilmadi")
        else:
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            button_location = types.KeyboardButton(text="Lokatsiyangizni yuboring", request_location=True)
            keyboard.add(button_location)
            await query.message.answer("Lokatsiya yuboring", reply_markup=keyboard)
    except Exception as e:
        print(f"Error: {e}")
        # Handle the error appropriately







@dp.message_handler(state=BuyAllProducts.PhoneNumber, content_types=[types.ContentType.TEXT, types.ContentType.CONTACT])
async def process_phone_number(message: types.Message, state: FSMContext):
    user_id = message.chat.id

    if message.content_type == types.ContentType.CONTACT:
        # Extract the phone number from the contact information
        phone_number = message.contact.phone_number
    else:
        # Check if the message starts with "+998"
        if message.text.startswith("+998"):
            # Extract the phone number
            phone_number = message.text
        else:
            # If the message does not start with "+998" and is not a contact, ask the user to enter a valid number
            await message.answer("+998 bilan boshlanadigan haqiqiy telefon raqamini kiriting yoki kontaktingizni baham ko'ring.")
            return

    # Save the user's phone number in the state
    await state.update_data(phone_number=phone_number)

    # Update the user's phone number in the database
    db.update_user_field(chat_id=user_id, key='phone_number', value=phone_number)

    shop_names = db.get_shop_name()  # Assuming this function returns a list of tuples (shop_id, shop_name)
    keyboard = types.InlineKeyboardMarkup()
    for shop_id, shop_name, _ in shop_names:
        button_shop = types.InlineKeyboardButton(text=shop_name, callback_data=f'shop_{shop_id}')
        keyboard.add(button_shop)

    await message.answer("Do'koningizning ismini tanlang", reply_markup=keyboard)
    await BuyAllProducts.ShopName.set()


@dp.message_handler(state=BuyAllProducts.Name)
async def process_name(message: types.Message, state: FSMContext):
    # Process the user's name
    user_name = message.text
    user_id = message.chat.id

    # Save the user's name in the state
    await state.update_data(name=user_name)

    # Update the user's first name in the database
    db.update_user_field(chat_id=user_id, key='first_name', value=user_name)

    # Create a keyboard with a button for sharing contact information
    button_phone = types.KeyboardButton(text="Raqamni yuborish", request_contact=True)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(button_phone)

    # Ask the user for their phone number
    await message.answer("Iltmos telefon raqamingizni kiriting", reply_markup=keyboard)

    # Move to the next state 'PhoneNumber'
    await BuyAllProducts.PhoneNumber.set()


@dp.message_handler(state=BuyAllProducts.PhoneNumber, content_types=[types.ContentType.TEXT, types.ContentType.CONTACT])
async def process_phone_number(message: types.Message, state: FSMContext):
    user_id = message.chat.id

    if message.content_type == types.ContentType.CONTACT:
        # Extract the phone number from the contact information
        phone_number = message.contact.phone_number
    else:
        # Check if the message starts with "+998"
        if message.text.startswith("+998"):
            # Extract the phone number
            phone_number = message.text
        else:
            # If the message does not start with "+998" and is not a contact, ask the user to enter a valid number
            await message.answer("+998 bilan boshlanadigan haqiqiy telefon raqamini kiriting yoki kontaktingizni baham ko'ring.")
            return

    # Save the user's phone number in the state
    await state.update_data(phone_number=phone_number)

    # Update the user's phone number in the database


    # Ask the user for their location
    # keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    # button_location = types.KeyboardButton(text="Lokatsiyangizni yuboring", request_location=True)
    # keyboard.add(button_location)
    # await message.answer("Lokatsiya yuboring", reply_markup=keyboard)

    # Move to the next state 'Location'
    await BuyAllProducts.ShopName.set()
#
#
#
@dp.message_handler(state=BuyAllProducts.Location, content_types=types.ContentType.LOCATION)
async def process_location(message: types.Message, state: FSMContext):

    user_id = message.from_user.id
    lang_id = db.get_user_language_id(user_id)

    keyboard_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)

    # Add the first button separately
    keyboard_menu.add(BTN_ORDER[lang_id])

    # Add the remaining buttons in pairs
    buttons_menu_row1 = [BTN_MY_ORDERS[lang_id], BTN_ABOUT_US[lang_id]]
    buttons_menu_row2 = [BTN_COMMENTS[lang_id], BTN_SETTINGS[lang_id], KORZINKA[lang_id]]

    keyboard_menu.add(*buttons_menu_row1)
    keyboard_menu.add(*buttons_menu_row2)

    # Process the user's location
    location = message.location
    longitude = location['longitude']
    latitude = location['latitude']

    # Save the user's location in the state
    await state.update_data(location=location)

    # Get the user's details from the state
    user_data = await state.get_data()
    user_id = message.chat.id
    user_name = user_data.get('name')
    user_phone_number = user_data.get('phone_number')
    user_location = user_data.get('location')

    # Finish the state machine
    await state.finish()

    # Send a confirmation message
    await message.answer("Buyurtmangiz uchun rahmat buyurmangiz qabul qilndi! Tez orada adminlar siz bilan bog'lanadi",reply_markup=keyboard_menu)

    # Retrieve all orders associated with the user_id
    orders = db.get_all_order_products(user_id)

    # Process the retrieved orders (you can customize this part based on your needs)
    for order in orders:
        order_id = order['id']
        amount = order['amount']
        product_id = order['product_id']
        price = order['product_price']

        # Print or use the details for each order
        print(f"Order ID: {order_id}, Amount: {amount}, Product ID: {product_id}, Price: {price}")

        # Check if an order with the same order_id already exists
        existing_order = db.get_orders_by_order_id(order_id)
        if existing_order:
            print(f"Order with ID {order_id} already exists. Skipping...")
            continue

        created_at = datetime.datetime.now()

        # Call the add_order function for each order
        db.add_order(user_id=user_id, status=1, product_id=product_id, latitude=latitude, longitude=longitude,
                     created_at=created_at, order_id=order_id)
        await inform_admin_about_order(order_id= order_id,user_id= user_id,product_ids=product_id,latitude= latitude,longitude= longitude, amounts=amount)


