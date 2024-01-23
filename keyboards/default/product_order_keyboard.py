from aiogram import types

from handlers.users.texts import SUM, NO_ORDERS, TEXT_MY_ORDERS, TEXT_ORDER_ACTIVE, ALL
from loader import dp, db


@dp.message_handler(text=['🛍 Buyurtmalarim', '🛍 Мои заказы'])
async def view_orders(message: types.Message):

    user_id = message.from_user.id
    print(user_id)
    lang_id = db.get_user_language_id(user_id)

    # Fetch orders using db.get_orders_by_user_and_status
    orders = db.get_orders_by_user_and_status(user_id)  # Assuming status 1 is for processed orders
    print(orders)
    if orders:
        total_sum = 0
        # Initialize a message to send order details
        orders_message = (f"<b>{TEXT_MY_ORDERS[lang_id]}</b>\n\n"
                          f"<i>{TEXT_ORDER_ACTIVE[lang_id]}</i>\n\n")

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
                    total_price = round(price * amount, 2)
                    total_sum += total_price

                    # Generate the response message for each product in the order
                    product_message = (f"{formatted_amount} x {product_name}\n")
                                       # f"Soni: {amount}\n"
                                       # f"Narxi: {price} {SUM[lang_id]}\n\n")


                    # Concatenate the product details to the overall message
                    orders_message += product_message

        # Send the consolidated message with all order details
        orders_message += f"\n{ALL[lang_id]} {round(total_sum, 2)}"

        await message.answer(text=orders_message, parse_mode='html')
    else:
        # If there are no orders, send a message to the user
        await message.answer(text=NO_ORDERS[lang_id])



