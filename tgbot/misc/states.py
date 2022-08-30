from aiogram.dispatcher.filters.state import StatesGroup, State


class AddProduct(StatesGroup):
    product_key = State()
    product_title = State()
    product_description = State()
    product_price = State()
    product_photo = State()
    product_need_name = State()
    product_need_phone_number = State()
    product_need_email = State()
    product_need_shipping_address = State()


class BSS(StatesGroup):
    amount_selection = State()
    specific_module_selection = State()
