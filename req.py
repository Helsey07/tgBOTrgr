from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
import requests

from DB.connect_db import connect_to_db
from State.states import StatesBot
from KeyBoard.keyboard import keyboard2

router = Router()
connection = connect_to_db()

async def get_exchange_rate(currency: str) -> float:
    try:
        url = f'http://195.58.54.159:8000/rate?currency={currency}'
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            return data['rate']
        elif response.status_code == 400:
            print(f"Ошибка: {data['message']}")
        elif response.status_code == 500:
            print(f"Ошибка: {data['message']}")
    except Exception as e:
        print(f'Ошибка при вводе обменного курса: {e}')
    return None

#обработчик команды /operations
@router.message(Command("operations"))
async def operations(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    connection = await connect_to_db()
    result = await connection.fetchval("SELECT * FROM users WHERE id = $1", user_id)

    if not result:
        await message.answer("Тебе нужно зарегистрироваться!")
        await state.clear()
    else:
        await message.answer("Выбери нужную операцию", reply_markup=keyboard2)
    await connection.close()

@router.message(F.text == 'RUB')
async def rub_operation(message: types.Message):
    currency = message.text.strip()
    user_id = message.from_user.id

    connection = await connect_to_db()
    results = await connection.fetch("SELECT * FROM operations WHERE chat_id = $1", user_id)
    if not results:
        await message.answer("Операции не найдены.")
    else:
        # Собираем строки в текстовое представление
        rows_text = "\n".join([f"ID: {row['id']}; Дата: {row['date']}; Сумма: {row['sum']} {currency}; "
                               f"Тип операции: {row['type_operation']}" for row in results])
        await message.answer(rows_text)
    await connection.close()

@router.message(F.text == 'USD')
async def usd_operation(message: types.Message):
    currency = message.text.strip()
    amount_currensy = await get_exchange_rate(currency)
    user_id = message.from_user.id

    connection = await connect_to_db()
    results = await connection.fetch("SELECT * FROM operations WHERE chat_id = $1", user_id)

    if not results:
        await message.answer("Операции не найдены.")
    else:
        await message.answer(f"Курс {currency} нынче составляет {amount_currensy}")
        # Собираем строки в текстовое представление
        rows_text = "\n".join([f"ID: {row['id']}; Дата: {row['date']}; Сумма: {round(float(row['sum'])/amount_currensy, 2)} {currency}; "
                               f"Тип операции: {row['type_operation']}" for row in results])
        await message.answer(rows_text)
    await connection.close()


@router.message(F.text == 'EUR')
async def eur_operation(message: types.Message):
    currency = message.text.strip()
    amount_currensy = await get_exchange_rate(currency)
    user_id = message.from_user.id

    connection = await connect_to_db()
    results = await connection.fetch("SELECT * FROM operations WHERE chat_id = $1", user_id)

    if not results:
        await message.answer("Операции не найдены.")
    else:
        await message.answer(f"Курс {currency} нынче составляет {amount_currensy}")
        # Собираем строки в текстовое представление
        rows_text = "\n".join([f"ID: {row['id']}; Дата: {row['date']}; Сумма: {round(float(row['sum'])/amount_currensy, 2)} {currency}; "
                               f"Тип операции: {row['type_operation']}" for row in results])
        await message.answer(rows_text)
    await connection.close()