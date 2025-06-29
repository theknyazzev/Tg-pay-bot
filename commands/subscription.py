import asyncio
import logging
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from payments import create_payment, check_payment
from db import add_subscription, get_all_subscriptions, remove_expired_subscription, get_subscription_status
from datetime import datetime, timedelta

async def handle_subscription(message: types.Message):
    user_id = message.from_user.id
    
    # Check if user already has an active subscription
    subscription_date = get_subscription_status(user_id)
    
    if subscription_date:
        # Check if subscription is still active
        if isinstance(subscription_date, str):
            expiration_date = datetime.fromisoformat(subscription_date)
        else:
            expiration_date = subscription_date
            
        current_time = datetime.now()
        
        if current_time < expiration_date:
            await message.answer(f"✅ У вас уже есть активная подписка до {expiration_date.strftime('%Y-%m-%d')}!")
            return
    
    # If no active subscription, create payment
    payment_url, label = create_payment(user_id)
    amount = 10

    pay_button = InlineKeyboardButton(text="To pay", url=payment_url)
    check_button = InlineKeyboardButton(text=f"I paid for it {amount} ₽", callback_data=f"check_payment_{label}_{amount}")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[pay_button], [check_button]])
    await message.answer("To pay for a subscription, click on the button below:", reply_markup=keyboard)

async def check_payment_status(callback_query: types.CallbackQuery):
    # Parse callback data: "check_payment_{user_id}_{timestamp}_{amount}"
    callback_data_parts = callback_query.data.split('_')
    
    # Reconstruct the label from parts 2 and 3 (user_id_timestamp)
    if len(callback_data_parts) >= 5:  # check_payment_{user_id}_{timestamp}_{amount}
        label = f"{callback_data_parts[2]}_{callback_data_parts[3]}"
        expected_amount = float(callback_data_parts[4])
    else:
        await callback_query.answer("Ошибка в данных платежа")
        return
    
    user_id = callback_query.from_user.id

    # Answer callback query first to remove loading state
    await callback_query.answer("Проверяем платеж...")

    print(f"Checking payment for label: {label}, expected amount: {expected_amount}")
    payment_successful = check_payment(label, expected_amount)

    if payment_successful:
        expiration_date = datetime.now() + timedelta(days=30)
        
        add_subscription(user_id, expiration_date.strftime("%Y-%m-%d"))
        
        await callback_query.message.edit_text(
            f"✅ Платеж успешно обработан! Ваша подписка активна до {expiration_date.strftime('%Y-%m-%d')}."
        )
    else:
        await callback_query.message.answer(
            "❌ Платеж не найден. Убедитесь, что оплата прошла успешно, и попробуйте снова через несколько минут."
        )

async def check_subscriptions_daily(bot):
    """Check and notify about expired subscriptions daily"""
    while True:
        try:
            current_time = datetime.now()
            expired_subscriptions = get_all_subscriptions()
            
            for user_id, expiration_date in expired_subscriptions:
                if isinstance(expiration_date, str):
                    expiration_date = datetime.fromisoformat(expiration_date.replace('Z', '+00:00'))
                
                if current_time >= expiration_date:
                    try:
                        await bot.send_message(
                            user_id, 
                            "⚠️ Your subscription has expired! Use /subscription to renew."
                        )
                        remove_expired_subscription(user_id)
                        logging.info(f"Notified user {user_id} about expired subscription")
                    except Exception as e:
                        logging.error(f"Failed to notify user {user_id}: {e}")
                        
        except Exception as e:
            logging.error(f"Error in subscription check: {e}")
        
        # Wait 24 hours
        await asyncio.sleep(24 * 60 * 60)

def start_subscription_checker(bot):
    """Start the subscription checker"""
    asyncio.create_task(check_subscriptions_daily(bot))
    logging.info("Subscription checker started")
