
import os
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from aiogram import Bot, Dispatcher, types
from config import BOT_TOKEN


# ======================
# HTTP SERVER (обязателен для Render)
# ======================
PORT = int(os.environ.get("PORT", 10000))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_server():
    print("HTTP SERVER STARTED")
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    server.serve_forever()


# ======================
# BOT
# ======================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler()
async def echo(msg: types.Message):
    print("MESSAGE:", msg.text)
    await msg.answer("Температура в Москве: 20°C")


async def main():
    print("BOT STARTED")

    while True:
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            print("WEBHOOK CLEARED")

            await dp.start_polling(bot)

        except Exception as e:
            print("POLLING ERROR:", e)
            await asyncio.sleep(5)


# ======================
# RUN
# ======================
if __name__ == "__main__":
    print("MAIN START")

    # старт сервера (обязательно для Render)
    thread = threading.Thread(target=run_server)
    thread.daemon = True
    thread.start()

    asyncio.run(main())
