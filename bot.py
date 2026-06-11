import asyncio

async def main():
    print("BOT STARTED")
    await bot.delete_webhook(drop_pending_updates=True)
    print("WEBHOOK DELETED")
    await dp.start_polling(bot)

if __name__ == "__main__":
    print("MAIN START")
    asyncio.run(main())
