from aiogram import types
from db import get_subscription_status
from datetime import datetime

async def handle_profile(message: types.Message):
    user_id = message.from_user.id
    subscription_status = get_subscription_status(user_id)
    
    if subscription_status:
        expiration_date = subscription_status.split("T")[0]
        status_text = f"Your subscription is active until: {expiration_date}"
    else:
        status_text = "The subscription is not active."

    profile_message = f"👤 User Profile:\n✅ ID: {user_id}\n✅ {status_text}"
    await message.answer(profile_message)
