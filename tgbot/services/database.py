from aiogram import Bot
from aiogram.types import User


async def add_user_payment(user: User, product: str, bot: Bot):
    async with bot['db'].cursor() as cur:
        await cur.execute(f"insert into payments(user_id, username, user_first_name, product) "
                          f"values ('{user.id}', '{user.username}', '{user.first_name}', '{product}')")


async def get_product_price(user_id: int, product: str, bot: Bot):
    async with bot['db'].cursor() as cur:
        # Берём цену из таблицы prices
        await cur.execute(f"select price from prices where product = '{product}'")
        price = (await cur.fetchone())[0]
        # Проверяем наличие персональной скидки
        await cur.execute(f"select discount from discounts where user_id = {user_id} and product = '{product}'")
        discount = await cur.fetchone()
        if discount is not None:
            price -= discount[0]
        return price

"""
1. Таблица с ценами - prices
product: varchar(255) (primary key), price: int
2. Таблица с персональными скидками - discounts
user_id: bigint, product: varchar(255), discount: int
3. Таблица с платежами - payments
user_id: bigint, username: varchar(255), user_first_name: varchar(255), product: varchar(255)
4. Таблица с теми, кто приобрел полный курс - full_pack_users
user_id: bigint (primary key)
"""
