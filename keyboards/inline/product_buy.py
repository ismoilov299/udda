import datetime
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, KeyboardButton, ReplyKeyboardMarkup
from handlers.users.admin import inform_admin_about_order
from handlers.users.texts import BTN_ORDER, BTN_MY_ORDERS, BTN_COMMENTS, BTN_SETTINGS, BTN_ABOUT_US, KORZINKA
from loader import dp, db, bot
from states.userStates import BuyAllProducts

@dp.callback_query_handler(lambda query: query.data == 'order_product', state='*')
async def buy_all_products_callback(query: CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    existing_user = db.get_user_by_chat_id(user_id)

    if existing_user:
        if existing_user[1] and existing_user[4]:
            # User has both shop name and location
            confirm_keyboard = types.InlineKeyboardMarkup()
            confirm_yes = types.InlineKeyboardButton(text="Ha", callback_data="confirm_yes")
            confirm_no = types.InlineKeyboardButton(text="Yo'q", callback_data="confirm_no")
            confirm_keyboard.add(confirm_yes, confirm_no)

            await query.message.edit_text(f"Do'koningizning nomi {existing_user[6]} to'g'ri mi?",
                                       reply_markup=confirm_keyboard)

            current_state = await state.get_state()
            if current_state != 'BuyAllProducts:ConfirmShopName':
                await BuyAllProducts.ConfirmShopName.set()
        else:
            # User is missing shop name or location
            current_state = await state.get_state()
            if current_state != 'BuyAllProducts:ShopName':
                await BuyAllProducts.ShopName.set()

                if not existing_user[1]:
                    # User is missing shop name, ask for it
                    await BuyAllProducts.Name.set()
                    await query.message.answer(
                        "Buyurtma qilish uchun Iltimos, ismingizni kiriting.")
                elif not existing_user[4]:
                    # User is missing location, ask for phone number
                    button_phone = types.KeyboardButton(text="Raqamni yuborish", request_contact=True)
                    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                    keyboard.add(button_phone)

                    # Ask the user for their phone number
                    await query.message.answer("Iltmos telefon raqamingizni kiriting", reply_markup=keyboard)
                    await BuyAllProducts.PhoneNumber.set()
    else:
        pass

# @dp.message_handler(state=BuyAllProducts.Location, content_types=types.ContentType.TEXT)
@dp.message_handler(state=BuyAllProducts.ShopName, content_types=types.ContentType.TEXT)
async def process_shop_selection(message: types.Message, state: FSMContext):

    try:
        user_id = message.from_user.id
        db.update_user_field(chat_id=user_id, key='shop_name', value=message.text)

        existing_user = db.get_user_by_chat_id(user_id)


        if existing_user[6] is None:
            await message.answer("Do'koningiz nomini kiriting")
        else:
            # Ask for the location directly if the shop name is already set
            comment_button = KeyboardButton(text="Yo'q")
            comment_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            comment_keyboard.add(comment_button)

            await message.answer("Komentariya qoldirasizmi?", reply_markup=comment_keyboard)
            await BuyAllProducts.Location.set()
    except Exception as e:
        print(f"Error: {e}")


@dp.callback_query_handler(lambda query: query.data.startswith('confirm_'), state=BuyAllProducts.ConfirmShopName)
async def process_confirm_shop_name(query: CallbackQuery, state: FSMContext):
    try:
        user_id = query.from_user.id
        confirmation = query.data.split('_')[1]

        if confirmation == 'yes':
            # If the user confirms, ask if they want to leave a comment
            comment_button = KeyboardButton(text="Yo'q")
            comment_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            comment_keyboard.add(comment_button)
            await query.message.delete()
            await query.message.answer("Komentariya qoldirasizmi?", reply_markup=comment_keyboard)

            # Set the state to capture the comment or location, depending on the user's choice
            await BuyAllProducts.Location.set()
        else:
            # If the user declines, ask them to choose the shop name again
            await query.message.delete()
            await query.message.answer("Iltimos, do'koningizning nomini qayta tanlang.")
            await BuyAllProducts.ShopName.set()

    except Exception as e:
        print(f"Error: {e}")

@dp.message_handler(state=BuyAllProducts.PhoneNumber, content_types=[types.ContentType.TEXT, types.ContentType.CONTACT])
async def process_phone_number(message: types.Message, state: FSMContext):
    user_id = message.chat.id

    if message.content_type == types.ContentType.CONTACT:
        phone_number = message.contact.phone_number
    else:
        if message.text.startswith("+998"):
            phone_number = message.text
        else:
            await message.answer("+998 bilan boshlanadigan haqiqiy telefon raqamini kiriting yoki kontaktingizni baham ko'ring.")
            return

    await state.update_data(phone_number=phone_number)
    db.update_user_field(chat_id=user_id, key='phone_number', value=phone_number)
    await message.answer("Do'koningizning nomini kiriting")

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
    await message.answer(f"{user_name} endi telefon raqamingizni kiriting", reply_markup=keyboard)

    # Move to the next state 'PhoneNumber'
    await BuyAllProducts.PhoneNumber.set()

@dp.message_handler(state=BuyAllProducts.Location, content_types=types.ContentType.TEXT)
async def process_buy(message: types.Message, state: FSMContext):
    print(message.text, ' location ')

    user_id = message.from_user.id
    lang_id = db.get_user_language_id(user_id)

    keyboard_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_menu.add(BTN_ORDER[lang_id])
    buttons_menu_row1 = [BTN_MY_ORDERS[lang_id], BTN_ABOUT_US[lang_id]]
    buttons_menu_row2 = [BTN_COMMENTS[lang_id], BTN_SETTINGS[lang_id], KORZINKA[lang_id]]
    keyboard_menu.add(*buttons_menu_row1)
    keyboard_menu.add(*buttons_menu_row2)

    orders = db.get_all_order_products(user_id)
    for order in orders:
        order_id = order['id']
        amount = order['amount']
        product_id = order['product_id']
        price = order['product_price']

        existing_order = db.get_orders_by_order_id(order_id)
        if existing_order:
            continue

        created_at = datetime.datetime.now()
        await state.finish()
        db.add_order(user_id=user_id, status=1, product_id=product_id, created_at=created_at, order_id=order_id)

    await inform_admin_about_order(user_id=user_id, order_ids=[order['id'] for order in orders],amounts=amount,comment=message.text,
                                   product_ids=[order['product_id'] for order in orders])

    await message.answer("Buyurtmangiz uchun rahmat buyurmangiz qabul qilndi! Tez orada adminlar siz bilan bog'lanadi", reply_markup=keyboard_menu)
