import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import os
PORT = int(os.environ.get("PORT", 10000))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_HEAD(self):  # ✅ добавь это
        self.send_response(200)
        self.end_headers()

def run_server():
    print("HTTP SERVER STARTING on port", PORT)  # 👈 лог запуска
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    server.serve_forever()

print("BOT FILE STARTED")
from aiogram import Bot, Dispatcher, types
#from aiogram.utils import executor
from config import BOT_TOKEN
print("TOKEN:", BOT_TOKEN)
from weather_api import get_weather,get_raw_weather

bot = Bot(token=BOT_TOKEN)
print("CREATED BOT")
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
from aiogram.utils.exceptions import TerminatedByOtherGetUpdates

async def main():
    print("START POLLING")  
    while True:
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            print("WEBHOOK DELETED")
            await dp.start_polling(bot)
        except TerminatedByOtherGetUpdates:
            print("Ждем конфликт...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    time.sleep(10)
    asyncio.run(main())
