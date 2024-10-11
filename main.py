import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from db import create_db
from commands.subscription import handle_subscription, check_payment_status
from commands.profile import handle_profile
from commands.start import handle_start
from config import TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

async def set_commands():
    commands = [
        types.BotCommand(command='/subscription', description='Pay to subscription'),
        types.BotCommand(command='/profile', description='Profile Information'),
        types.BotCommand(command='/start', description='Start message')
    ]
    await bot.set_my_commands(commands)

async def on_startup(dp):
    create_db()
    await set_commands()
    logging.info("The bot launched!")

if __name__ == '__main__':
    dp.register_message_handler(handle_subscription, commands=['subscription'])
    dp.register_message_handler(handle_start, commands=['start'])
    dp.register_message_handler(handle_profile, commands=['profile'])
    dp.register_callback_query_handler(check_payment_status, lambda c: c.data.startswith('check_payment_'))
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
