import time

from aiogram import Bot
from sqlalchemy import select

from tgbot.misc.models import Payment, FullPackUser, Discount, Product, Misc


async def add_payment(user_id: int, product: str, bot: Bot):
    db_session = bot['db']
    async with db_session() as session:
        user_id_time = "_".join([str(user_id), str(int(time.time()))])
        await session.merge(Payment(product=product, user_id_time=user_id_time))
        await session.commit()


async def add_full_pack_user(user_id: int, user_name: str, bot: Bot):
    db_session = bot['db']
    async with db_session() as session:
        await session.merge(FullPackUser(user_id=user_id, user_name=user_name))
        await session.commit()


async def get_product(user_id: int, product_key: str, bot: Bot):
    db_session = bot['db']
    async with db_session() as session:
        product_sql = select(Product).where(Product.key == product_key)
        product_request = await session.execute(product_sql)

        product = product_request.scalar()

        discount_sql = select(Discount).where(Discount.user_id == user_id).where(Discount.product == product_key)
        discount_request = await session.execute(discount_sql)

        discount_obj = discount_request.scalar()

        if discount_obj is not None:
            product.price -= discount_obj.discount
            await session.delete(discount_obj)
            await session.commit()

        return product


async def get_full_pack_users_id(bot: Bot):
    db_session = bot['db']
    async with db_session() as session:
        request = await session.execute(select(FullPackUser.user_id))
        return request.scalars().all()


async def add_product(product: Product, bot: Bot):
    db_session = bot['db']
    async with db_session() as session:
        await session.merge(product)
        await session.commit()


async def get_bss_chat(bot: Bot):
    db_session = bot['db']
    async with db_session() as session:
        sql = select(Misc).where(Misc.key == 'bss_chat')
        chat_id = await session.execute(sql)
        return chat_id.scalar().value


async def set_bss_chat(chat_id: int, bot: Bot):
    db_session = bot['db']
    async with db_session() as session:
        await session.merge(Misc(key='bss_chat', value=str(chat_id)))
        await session.commit()
