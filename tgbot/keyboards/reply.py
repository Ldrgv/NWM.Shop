from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# Выбор первого действия
def get_start():
    buttons = [
        KeyboardButton(text='Бюро счастливых семей'),
        KeyboardButton(text='Расписание молитв (СПб)'),
        KeyboardButton(text='Halal map')
    ]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(*buttons)
    return keyboard


# Выбор количества модулей
def get_amount_selection():
    buttons = [
        KeyboardButton(text='1'),
        KeyboardButton(text='3'),
        KeyboardButton(text='<')
    ]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(*buttons)
    return keyboard


# Выбор конкретного модуля
def get_specific_module_selection():
    buttons = [
        KeyboardButton(text=f'{num}') for num in range(1, 4)
    ]
    buttons.append(KeyboardButton(text='<'))
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    keyboard.add(*buttons)
    return keyboard
