import asyncio
import aiomysql
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from tgbot.config import load_config
from tgbot.filters.admin import AdminFilter
from tgbot.handlers.errors import register_errors
from tgbot.handlers.admin import register_admin
from tgbot.handlers.user import register_user
from tgbot.misc.models import Base

logger = logging.getLogger(__name__)


def register_all_middlewares(dp):
    dp.setup_middleware(LoggingMiddleware())


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    register_errors(dp)
    register_admin(dp)
    register_user(dp)


async def main():
    # Настраиваем логирование
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")

    # Загружаем переменные окружения
    config = load_config(".env")

    # Настраиваем SQLAlchemy
    engine = create_async_engine(
        f"postgresql+asyncpg://{config.db.user}:{config.db.password}@{config.db.host}/{config.db.name}",
    )

    # Создаём нужные таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher(bot=bot, storage=MemoryStorage())
    db = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    bot['config'] = config
    bot['db'] = db

    register_all_middlewares(dp)
    register_all_filters(dp)
    register_all_handlers(dp)

    # start
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
