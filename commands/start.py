from aiogram import types 

async def handle_start(message: types.Message):
    start_message = f"Hi! Use: \n/subscription"
    await message.answer(start_message)
