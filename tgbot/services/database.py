import time

from aiogram import Bot
from sqlalchemy import select

from tgbot.misc.models import Payment, FullPackUser, Price, Discount


async def add_payment(user_id: int, product: str, bot: Bot):
    db_session = bot['db']
    async with db_session() as session:
        user_id_time = "_".join([str(user_id), str(int(time.time()))])
        await session.merge(Payment(product=product, user_id_time=user_id_time))
        await session.commit()


async def add_full_pack_user(user_id: int, user_name: str, chat_id: int, bot: Bot):
    db_session = bot['db']
    async with db_session() as session:
        await session.merge(FullPackUser(user_id=user_id, user_name=user_name, chat_id=chat_id))
        await session.commit()


async def get_product_price(user_id: int, product: str, bot: Bot):
    db_session = bot['db']
    async with db_session() as session:
        price_sql = select(Price).where(Price.product == product)
        price_request = await session.execute(price_sql)

        price = price_request.scalar().price

        discount_sql = select(Discount).where(Discount.user_id == user_id).where(Discount.product == product)
        discount_request = await session.execute(discount_sql)

        discount_obj = discount_request.scalar()

        if discount_obj is not None:
            price -= discount_obj.discount
            await session.delete(discount_obj)
            await session.commit()

        return price


async def get_full_pack_users_chat_id(bot: Bot):
    db_session = bot['db']
    async with db_session() as session:
        request = await session.execute(select(FullPackUser.chat_id))
        chats = request.scalars().all()
        return chats

