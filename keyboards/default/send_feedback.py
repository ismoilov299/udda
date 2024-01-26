from aiogram import types
from aiogram.contrib.middlewares import logging

from loader import bot
admin_chat_id = -1002064650084

async def send_feedback_to_admin(feedback: str, feedback_id: int):
    try:
        user = await bot.get_chat(feedback_id)
        user_link = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
        user_link = f'<a href="https://t.me/{user.username}">{user_link}</a>'

        message_text = f"<b>Yangi fikr yoki shikoyat:</b>\n\n{user_link} habar:\n\n{feedback}"

        await bot.send_message(chat_id=admin_chat_id, text=message_text, parse_mode=types.ParseMode.HTML)

    except Exception as e:
        logging.error(f"Error sending message to the admin: {e}")

async def send_suggestion_to_admin(suggestion: str, suggestion_id: int):
    try:
        user = await bot.get_chat(suggestion_id)
        user_link = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
        user_link = f'<a href="https://t.me/{user.username}">{user_link}</a>'

        message_text = f"<b>New suggestion:</b>\n\n{user_link} suggested:\n\n{suggestion}"

        await bot.send_message(chat_id=admin_chat_id, text=message_text, parse_mode=types.ParseMode.HTML)

    except Exception as e:
        logging.error(f"Error sending suggestion to the admin: {e}")
