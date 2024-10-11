from aiogram import types
from payments import create_payment, check_payment
from db import add_subscription
from datetime import datetime, timedelta

async def handle_subscription(message: types.Message):
    user_id = message.from_user.id
    payment_url, label = create_payment(user_id)
    amount = 10

    keyboard = types.InlineKeyboardMarkup()
    pay_button = types.InlineKeyboardButton("To pay", url=payment_url)
    check_button = types.InlineKeyboardButton(f"I paid for it {amount} ₽", callback_data=f"check_payment_{label}_{amount}")

    keyboard.add(pay_button, check_button)
    await message.answer("To pay for a subscription, click on the button below:", reply_markup=keyboard)

async def check_payment_status(callback_query: types.CallbackQuery):
    callback_data_parts = callback_query.data.split('_')
    label = callback_data_parts[2]
    expected_amount = float(callback_data_parts[3])
    user_id = callback_query.from_user.id

    payment_successful = check_payment(label, expected_amount)

    if payment_successful:
        expiration_date = datetime.now() + timedelta(days=30)
        
        add_subscription(user_id, expiration_date.strftime("%Y-%m-%d"))
        
        await callback_query.message.answer(f"The payment was successful! Your subscription is activated before {expiration_date.strftime('%Y-%m-%d')}.")
    else:
        await callback_query.message.answer("The payment was not found. Try again later.")
