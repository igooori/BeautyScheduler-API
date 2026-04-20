import asyncio
from aiogram import Bot,Dispatcher
# from config import TOKEN
from app.services import app
import uvicorn

async def main():
    dp = Dispatcher()
    # bot = Bot(token=TOKEN)

    config = uvicorn.Config(app, host='0.0.0.0', port=4000, log_level='info')
    server = uvicorn.Server(config)
    print('Бот запускаеться')
    # dp.include_router()

    await asyncio.gather(
        # dp.start_polling(bot),
        server.serve()
    )

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот остановлен')
if __name__ == '__main__':
    uvicorn.run(app,host='0.0.0.0', port=4000)