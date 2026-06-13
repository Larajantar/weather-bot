import os
import asyncio
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
from config import BOT_TOKEN
loop = None

# ======================
# PORT (для Render)
# ======================
PORT = int(os.environ.get("PORT", 10000))
BASE_URL = os.environ.get("BASE_URL")  # например https://weather-bot-xam1.onrender.com
if not BASE_URL:
    raise ValueError("BASE_URL is not set")
BASE_URL = BASE_URL.rstrip("/")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{BASE_URL}{WEBHOOK_PATH}"

# ======================
# HTTP SERVER
# ======================
class Handler(BaseHTTPRequestHandler):    
    def do_POST(self):
        if self.path == WEBHOOK_PATH:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            
            data = json.loads(body.decode("utf-8"))
            update = Update(**data)
            update.bot = bot
            
            loop.call_soon_threadsafe(
                asyncio.create_task,
                dp.process_update(update)
            )

            self.send_response(200)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        print("HTTP GET", flush=True)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_http_server():
    print("HTTP SERVER STARTED", flush=True)
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    server.serve_forever()


# ======================
# BOT
# ======================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler()
async def echo(msg: types.Message):
    print("MESSAGE:", msg.text, flush=True)
    await msg.answer("Температура в Москве: 20°C")


# ======================
# MAIN
# ======================

async def main():
    global loop
    loop = asyncio.get_running_loop()  
    
    print("BOT STARTED", flush=True)

    await bot.delete_webhook(drop_pending_updates=True)

    # ставим webhook
    await bot.set_webhook(WEBHOOK_URL)
    print(f"WEBHOOK SET: {WEBHOOK_URL}", flush=True)

    # запускаем сервер
    import threading
    threading.Thread(target=run_http_server, daemon=True).start()

    # держим процесс живым
    while True:
        await asyncio.sleep(3600)


# ======================
# RUN
# ======================
if __name__ == "__main__":
    print("MAIN START", flush=True)
    asyncio.run(main())
