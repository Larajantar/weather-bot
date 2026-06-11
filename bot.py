import asyncio
from aiogram import Bot, Dispatcher, types
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler()
async def echo(msg: types.Message):
    print("MESSAGE RECEIVED:", msg.text)
    await msg.answer("Температура в Москве: 20°C")  # статичный ответ


async def main():
    print("BOT STARTED")

    await bot.delete_webhook(drop_pending_updates=True)
    print("WEBHOOK CLEARED")

    await dp.start_polling(bot)


if __name__ == "__main__":
    print("MAIN START")
    asyncio.run(main())
