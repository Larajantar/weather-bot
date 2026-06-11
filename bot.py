from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from config import BOT_TOKEN
from weather_api import get_weather,get_raw_weather

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
user_compare = {}

@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Москва", "Одинцово", "Питер", "Гатчина")
    kb.add("Сравнить города")

    await msg.answer("Выбери город или режим:", reply_markup=kb)

#выбор города для сравнения
@dp.message_handler(lambda msg: msg.text == "Сравнить города")
async def compare_start(msg: types.Message):
    user_compare[msg.from_user.id] = []
    await msg.answer("Выбери первый город")


@dp.message_handler(lambda msg: msg.text in ["Москва", "Одинцово", "Питер", "Гатчина"])
async def handle_city(msg: types.Message):
    user_id = msg.from_user.id

    # ✅ если в режиме сравнения
    if user_id in user_compare:
        user_compare[user_id].append(msg.text)

        if len(user_compare[user_id]) == 1:
            await msg.answer("Выбери второй город")
            return

        elif len(user_compare[user_id]) == 2:
            city1, city2 = user_compare[user_id]

            t1, h1 = get_raw_weather(city1)
            t2, h2 = get_raw_weather(city2)

            temp_diff = round(t1 - t2, 1)
            hum_diff = round(h1 - h2, 1)

            result = ""

            if temp_diff > 0:
                result += f"{city1} теплее города {city2} на {abs(temp_diff)}°C\n"
            else:
                result += f"{city2} теплее города {city1} на {abs(temp_diff)}°C\n"

            if hum_diff > 0:
                result += f"Влажность выше на {abs(hum_diff)}%"
            else:
                result += f"Влажность ниже на {abs(hum_diff)}%"

            await msg.answer(result)

            # ✅ сброс
            del user_compare[user_id]
            return

    # ✅ ВАЖНО: обычная погода (вынесено наружу!)
    result = get_weather(msg.text)
    await msg.answer(result)

#если ошибка
@dp.message_handler()
async def fallback(msg: types.Message):
    await msg.answer("Выбери кнопку ниже")

#запуск
import asyncio
import time

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    time.sleep(10)
    asyncio.run(main())
