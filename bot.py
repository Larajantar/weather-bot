import os                  # работа с переменными окружения (PORT, BASE_URL)
import asyncio              # асинхронный движок Python (используется aiogram)
import json                  # для обработки JSON (Telegram шлёт JSON)
import aiogram 
from http.server import BaseHTTPRequestHandler, HTTPServer  # встроенный HTTP сервер
from weather_api import get_weather,get_raw_weather

from aiogram import Bot, Dispatcher, types      # библиотека Telegram-бота
from config import BOT_TOKEN                  # токен бота из файла config
print(aiogram.__version__, flush=True)

loop = None  
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
user_compare = {}    

# ======================
# PORT (для Render)
# ======================
PORT = int(os.environ.get("PORT", 10000))              # берём порт из окружения или ставим 10000
BASE_URL = os.environ.get("BASE_URL")                  # базовый URL (например https://...onrender.com)

if not BASE_URL:  # если не задан
    raise ValueError("BASE_URL is not set")             # падаем с ошибкой

BASE_URL = BASE_URL.rstrip("/")                          # убираем слэш в конце (чтобы не было //)
WEBHOOK_PATH = "/webhook"                              # путь, куда Telegram будет слать сообщения
WEBHOOK_URL = f"{BASE_URL}{WEBHOOK_PATH}"              # полный URL webhook

class Handler(BaseHTTPRequestHandler):                  # класс обработки HTTP запросов
    
    def do_POST(self):                                      # вызывается при POST запросе (Telegram использует POST)
        if self.path == WEBHOOK_PATH:                    # если запрос пришёл на /webhook
            print("WEBHOOK HIT", flush=True)
            
            content_length = int(self.headers.get("Content-Length", 0))  # длина тела запроса
            body = self.rfile.read(content_length)                    # читаем тело запроса (байты)
            
            data = json.loads(body.decode("utf-8"))                    # превращаем JSON → dict            
            update = types.Update(**data)
            
            def process():
                Bot.set_current(bot)
                Dispatcher.set_current(dp)
                return dp.process_update(update)
            
            loop.call_soon_threadsafe(
                asyncio.create_task,
                process()
            )

            self.send_response(200)                                      # отвечаем HTTP 200 (успех)
            self.end_headers()                                      # заканчиваем ответ

        else:  # если путь не /webhook
            self.send_response(404)                                      # говорим "не найдено"
            self.end_headers()

    def do_GET(self):                                      			# обработка GET (Render проверяет, жив ли сервер)
        print("HTTP GET", flush=True)                    			# лог
        self.send_response(200)                                      # отвечаем OK
        self.end_headers()
        self.wfile.write(b"OK")                                      # отправляем текст "OK"

    def do_HEAD(self):                                      	# обработка HEAD (Render иногда шлёт)
        self.send_response(200)                                      # отвечаем OK
        self.end_headers()

# функция запуска HTTP сервера
def run_http_server():
    print("HTTP SERVER STARTED", flush=True)                    # лог старта
    server = HTTPServer(("0.0.0.0", PORT), Handler)  			# создаём сервер: 0.0.0.0 = слушаем все интерфейсы, PORT = порт, Handler = обработчик
    server.serve_forever()                                      # запуск сервера (бесконечный цикл)

@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Москва", "Одинцово", "Питер", "Гатчина")
    kb.add("Сравнить города")

    await bot.send_message(
        chat_id=msg.chat.id,
        text="Выбери город или режим:",
        reply_markup=kb
    )

#выбор города для сравнения
@dp.message_handler(lambda msg: msg.text == "Сравнить города")
async def compare_start(msg: types.Message):
    user_compare[msg.from_user.id] = []

    await bot.send_message(
        chat_id=msg.chat.id,
        text="Выбери первый город"
    )

@dp.message_handler(lambda msg: msg.text in ["Москва", "Одинцово", "Питер", "Гатчина"])
async def handle_city(msg: types.Message):
    user_id = msg.from_user.id

    if user_id in user_compare:
        user_compare[user_id].append(msg.text)

        if len(user_compare[user_id]) == 1:
            await bot.send_message(
                chat_id=msg.chat.id,
                text="Выбери второй город"
            )
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

            await bot.send_message(
                chat_id=msg.chat.id,
                text=result
            )

            del user_compare[user_id]			# ✅ сброс
            return

    result = get_weather(msg.text)				# ✅ ВАЖНО: обычная погода (вынесено наружу!)
    await bot.send_message(
        chat_id=msg.chat.id,
        text=result
    )

#если ошибка
@dp.message_handler()
async def fallback(msg: types.Message):
    await bot.send_message(
        chat_id=msg.chat.id,
        text="Выбери кнопку ниже"
    )

async def main():
    global loop                                          # говорим, что будем использовать глобальную переменную
    loop = asyncio.get_running_loop()                      # сохраняем текущий event loop
    Bot.set_current(bot)                                           # установить bot в контекст
    Dispatcher.set_current(dp)
    print("BOT STARTED", flush=True)                          # лог старта

    await bot.delete_webhook(drop_pending_updates=True)          # удаляем старый webhook (если был), drop_pending_updates=True = очищаем очередь сообщений

    await bot.set_webhook(WEBHOOK_URL)                          # устанавливаем webhook → Telegram будет слать POST-запросы сюда

    print(f"WEBHOOK SET: {WEBHOOK_URL}", flush=True)  # выводим URL webhook

    # запускаем HTTP сервер в отдельном потоке
    import threading
    threading.Thread(target=run_http_server, daemon=True).start()

    # держим программу живой (иначе она завершится)
    while True:
        await asyncio.sleep(3600)                      # "спим", но процесс живёт

# ======================
# RUN
# ======================
if __name__ == "__main__":                          # если файл запускается напрямую
    print("MAIN START", flush=True)                  # лог

    asyncio.run(main())                              # запускаем main() через asyncio
