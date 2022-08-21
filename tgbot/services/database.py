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

        discount_sql = select(Discount).where(Discount.user_id == user_id)
        discount_request = await session.execute(discount_sql)

        discount_obj = discount_request.scalar()

        if discount_obj is not None:
            price -= discount_obj.discount

        return price


async def get_full_pack_users_chat_id(bot: Bot):
    db_session = bot['db']
    async with db_session() as session:
        request = await session.execute(select(FullPackUser))
        chats = [full_pack_user.chat_id for full_pack_user in request.scalars()]
        return chats

"""
1. Таблица с ценами - prices
product: varchar(255) (primary key), price: int
2. Таблица с персональными скидками - discounts
user_id: bigint, product: varchar(255), discount: int
3. Таблица с платежами - payments
user_id: bigint, username: varchar(255), user_first_name: varchar(255), product: varchar(255)
4. Таблица с теми, кто приобрел полный курс - full_pack_users
user_id: bigint (primary key), user_first_name varchar(255), user_chat_id bigint
"""
