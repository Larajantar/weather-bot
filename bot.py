import os
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer

from aiogram import Bot, Dispatcher, types
from config import BOT_TOKEN


# ======================
# PORT (для Render)
# ======================
PORT = int(os.environ.get("PORT", 10000))


# ======================
# HTTP SERVER
# ======================
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("HTTP GET")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_HEAD(self):
        print("HTTP HEAD")
        self.send_response(200)
        self.end_headers()


def run_http_server():
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


# ======================
# MAIN
# ======================

async def main():
    print("BOT STARTED")

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("WEBHOOK CLEARED")

        loop = asyncio.get_running_loop()
        loop.run_in_executor(None, run_http_server)

        print("START POLLING")

        await dp.start_polling(bot)

    except Exception as e:
        print("MAIN ERROR:", e)
        raise

# ======================
# RUN
# ======================
if __name__ == "__main__":
    print("MAIN START")
    asyncio.run(main())
