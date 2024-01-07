from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.default.send_feedback import send_feedback_to_admin
from loader import dp, db
from states.userStates import FeedbackState


@dp.message_handler(text=['✍ Fikr bildirish', '✍ Отзыв'])
async def add_comment(message: types.Message):
    # Prompt the user to write their feedback
    await message.answer('Fikr va takliflaringizni yozib qoldiring')

    # Set the state to handle the user's feedback
    await FeedbackState.WaitingForFeedback.set()


@dp.message_handler(state=FeedbackState.WaitingForFeedback)
async def process_feedback(message: types.Message, state: FSMContext):
    # Get the user details
    user_id = message.from_user.id
    username = message.from_user.first_name

    # Extract feedback text from the message
    feedback_text = message.text

    # Add the feedback as a comment in the database
    db.add_comment(user_id=user_id, comment_text=feedback_text, username=username)

    # Send a confirmation message to the user
    await message.answer("Fikr va takliflaringiz uchun rahmat!")

    # Send the feedback to the admin
    await send_feedback_to_admin(feedback=feedback_text, feedback_id=user_id)

    # Reset the state after processing the feedback
    await state.finish()