import asyncio
import logging

from aiohttp import web
import ssl

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from notify_admin import on_startup_notify
from database.models import async_main
from config_data.config_data import Config, load_config

from handlers import start_handler
from handlers.admin_handlers import add_or_delete_ideas
from handlers.user_handlers import generate_handler, money_handler, prompts_handler, help_handler, referal_handler
from handlers.user_handlers.money_handler import handle_webhook

# Инициализируем logger
logger = logging.getLogger(__name__)

# Функция конфигурирования и запуска бота
async def main():
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,

        filename="py_log.log",
        filemode='w',
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    #Регистрация роутеров
    # Старт
    dp.include_router(start_handler.router)

    # Админ
    dp.include_router(add_or_delete_ideas.router)

    # Пользователь
    dp.include_router(money_handler.router)
    dp.include_router(prompts_handler.router)
    dp.include_router(help_handler.router)
    dp.include_router(referal_handler.router)
    dp.include_router(generate_handler.router)


    await on_startup_notify(bot=bot)
    await async_main()

    web_app = web.Application()
    web_app.router.add_post("/webhook", handle_webhook)
    web_app['bot'] = bot

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    try:
        ssl_context.load_cert_chain(
            certfile='/etc/letsencrypt/live/viva-test.mashkovtemaa.ru/fullchain.pem',
            keyfile='/etc/letsencrypt/live/viva-test.mashkovtemaa.ru/privkey.pem'
        )
    except FileNotFoundError:
        logging.error("SSL certificate files not found.  HTTPS will not work.")
        ssl_context = None

    runner = web.AppRunner(web_app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", 7000, ssl_context=ssl_context)
    await site.start()
    logging.info('Webhook server started on port 8000 with HTTPS')

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
