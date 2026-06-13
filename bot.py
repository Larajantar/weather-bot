import os                  # работа с переменными окружения (PORT, BASE_URL)
import asyncio              # асинхронный движок Python (используется aiogram)
import json                  # для обработки JSON (Telegram шлёт JSON)
from http.server import BaseHTTPRequestHandler, HTTPServer  # встроенный HTTP сервер

from aiogram import Bot, Dispatcher, types      # библиотека Telegram-бота
from aiogram.types import Update              # объект входящего события от Telegram
from config import BOT_TOKEN                  # токен бота из файла config

loop = None                                  # сюда сохраним главный asyncio loop (нужен для потоков)

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

# ======================
# HTTP SERVER
# ======================
class Handler(BaseHTTPRequestHandler):                  # класс обработки HTTP запросов
    
    def do_POST(self):                                      # вызывается при POST запросе (Telegram использует POST)
        if self.path == WEBHOOK_PATH:                    # если запрос пришёл на /webhook

            content_length = int(self.headers.get("Content-Length", 0))  # длина тела запроса

            body = self.rfile.read(content_length)                    # читаем тело запроса (байты)

            data = json.loads(body.decode("utf-8"))                    # превращаем JSON → dict

            update = Update(**data)                                      # создаём объект Update из данных

            # передаём обработку update в главный async loop
            loop.call_soon_threadsafe(
                asyncio.create_task,                                      # создаём асинхронную задачу
                dp.feed_update(bot, update)                            # передаём update в aiogram
            )

            self.send_response(200)                                      # отвечаем HTTP 200 (успех)
            self.end_headers()                                      # заканчиваем ответ

        else:  # если путь не /webhook
            self.send_response(404)                                      # говорим "не найдено"
            self.end_headers()

    def do_GET(self):                                      # обработка GET (Render проверяет, жив ли сервер)
        print("HTTP GET", flush=True)                    # лог

        self.send_response(200)                                      # отвечаем OK
        self.end_headers()

        self.wfile.write(b"OK")                                      # отправляем текст "OK"

    def do_HEAD(self):                                      # обработка HEAD (Render иногда шлёт)
        self.send_response(200)                                      # отвечаем OK
        self.end_headers()

# функция запуска HTTP сервера
def run_http_server():
    print("HTTP SERVER STARTED", flush=True)                    # лог старта

    server = HTTPServer(("0.0.0.0", PORT), Handler)  
                                                                # создаём сервер:
                                                                # 0.0.0.0 = слушаем все интерфейсы
                                                                # PORT = порт
                                                                # Handler = обработчик

    server.serve_forever()                                      # запуск сервера (бесконечный цикл)


# ======================
# BOT
# ======================
bot = Bot(token=BOT_TOKEN)                                      # создаём объект бота

dp = Dispatcher(bot)                                      # создаём диспетчер (обрабатывает события)

                                                                        # обработчик всех входящих сообщений
@dp.message_handler()
async def echo(msg: types.Message):  
    print("MESSAGE:", msg.text, flush=True)                            # вывод текста сообщения в лог

    await msg.answer("Температура в Москве: 20°C")                    # отправка ответа пользователю


# ======================
# MAIN
# ======================
async def main():
    global loop                                          # говорим, что будем использовать глобальную переменную

    loop = asyncio.get_running_loop()                      # сохраняем текущий event loop

    print("BOT STARTED", flush=True)                          # лог старта

    await bot.delete_webhook(drop_pending_updates=True)  
    # удаляем старый webhook (если был)
    # drop_pending_updates=True = очищаем очередь сообщений

    await bot.set_webhook(WEBHOOK_URL)  
    # устанавливаем webhook → Telegram будет слать POST-запросы сюда

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
