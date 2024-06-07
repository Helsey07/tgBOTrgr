import asyncio
import os
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command, StateFilter
import asyncpg
from aiogram.types import BotCommand, BotCommandScopeDefault
import datetime
import re
import requests

#извлечение токена из переменной окружения и инициализация объекта бота

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=bot_token)
storage = MemoryStorage()

#Настройка диспетчера и роутов

dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

async def connect_to_db():
    connection = await asyncpg.connect(
        host='127.0.0.1',
        port='5432',
        database='tgbot',
        user='postgres',
        password='egor2003'
    )
    return connection

#Определение состояний FSM

class StatesBot(StatesGroup):
    login_entry_for_reg = State()

    money = State()
    date = State()

    SelectButton = State()

    operationIdentifier = State()
    replacementAmount = State()

kb = [
    [types.KeyboardButton(text='ДОХОД')],
    [types.KeyboardButton(text='РАСХОД')],
]
keyboard = types.ReplyKeyboardMarkup(keyboard=kb)

kb2 = [
    [types.KeyboardButton(text='RUB')],
    [types.KeyboardButton(text='EUR')],
    [types.KeyboardButton(text='USD')],
]
keyboard2 = types.ReplyKeyboardMarkup(keyboard=kb2)

comands = [
    BotCommand(command='/reg', description='Регистрация'),
    BotCommand(command='/add_operation', description='Добавление новой операции'),
    BotCommand(command='/operations', description='Просмотр операций'),
    BotCommand(command='/update_operation', description='Обновление суппы операции')
]

#обработчик команды /start
@router.message(Command("start"))
async def start_command(message: types.Message):
        await message.answer("Привет, ГАНСТЕР! Выбери нужную тебе команду")
#обработчик команды /reg
@router.message(Command("reg"))
async def reg(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    print(user_id)

    connection = await connect_to_db()
    result = await connection.fetchval("SELECT * FROM users WHERE id = $1", user_id)

    if result:
        await message.answer("Ты уже зарегистрирован 🤬")
        await state.clear()
    else:
        await message.answer("Напиши свой логин  👀")
        await state.set_state(StatesBot.login_entry_for_reg)
    await connection.close()

@router.message(StateFilter(StatesBot.login_entry_for_reg))
async def set_currency_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    user_id = message.from_user.id

    connection = await connect_to_db()
    availabilityLogin = await connection.fetchrow("SELECT * FROM users WHERE name = $1", name)

    if availabilityLogin:
        await message.answer("Лонин уже занят... Придумай уникальный 🤬")
    else:
        await connection.fetchrow("INSERT INTO users (id, name) VALUES ($1, $2)", user_id, name)
        await message.answer("Теперь ты с нами!!!!  🤪")
        await state.clear()
    await connection.close()
# ___________________________________________________________________________________________________________________
#обработчик команды /add_operation

@router.message(Command("add_operation"))
async def add_operation(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    connection = await connect_to_db()
    result = await connection.fetchval("SELECT * FROM users WHERE id = $1", user_id)

    if not result:
        await message.answer("Ты не зарегистрирован 🤬")
    else:
        await message.answer("Выбери нужную операцию", reply_markup=keyboard)

    await connection.close()

@router.message(F.text == 'РАСХОД')
async def add_operation(message: types.Message, state: FSMContext):
    operation_type = message.text.strip()
    user_id = message.from_user.id
    if operation_type:
        await message.answer("Введи сумму операции в рублях")
        await state.update_data(operation_type=operation_type)
        await state.set_state(StatesBot.money)
    else:
        await message.answer("Выберите команду из предложенных")

@router.message(F.text == 'ДОХОД')
async def add_operation(message: types.Message, state: FSMContext):
    operation_type = message.text.strip()
    user_id = message.from_user.id
    if operation_type:
        await message.answer("Введи сумму операции в рублях")
        await state.update_data(operation_type=operation_type)
        await state.set_state(StatesBot.money)
    else:
        await message.answer("Выберите команду из предложенных")

@router.message(StateFilter(StatesBot.money))
async def money(message: types.Message, state: FSMContext):
    try:
        print('Состояние money')
        money = float(message.text.strip())
        await message.answer("Введи дату")
        await state.update_data(amount=money)
        await state.set_state(StatesBot.date)
    except ValueError:
        await message.answer("Введите корректную сумму операции в рублях (число)")

@router.message(StateFilter(StatesBot.date))
async def date(message: types.Message, state: FSMContext):
    date_str = message.text.strip()
    # Проверяем формат даты (Регулярное выражение)
    if re.match(r'\d{2}\.\d{2}\.\d{4}', date_str):
        try:
            # Пробуем преобразовать строку в объект datetime
            date = datetime.datetime.strptime(date_str, '%d.%m.%Y')

            await state.update_data(date=date)
            data = await state.get_data()

            operation_type = data.get('operation_type')  # Получение типа операции
            amount = data.get('amount')
            date = data.get('date')
            user_id = message.from_user.id
            try:
                print('Попытка сохранения в базу данных')
                connection = await connect_to_db()
                await connection.fetchrow(
                    "INSERT INTO operations (date, sum, chat_id, type_operation) VALUES ($1, $2, $3, $4)",
                    date, amount, user_id, operation_type)
                await message.answer("Сохранение прошло успешно")
                await state.clear()
                await connection.close()
            except Exception:
                await message.answer("ЧО ТО ПОШЛО НЕ ТАК")
        except ValueError:
            await message.answer("Введите корректную дату в формате ДД.ММ.ГГГГ1")
    else:
        await message.answer("Введите дату в формате ДД.ММ.ГГГГ2")
# ___________________________________________________________________________________________________________________
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
        await state.set_state(StatesBot.SelectButton)
    await connection.close()

@router.message(F.text == 'RUB')
async def rub_operation(message: types.Message, state: FSMContext):
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
async def usd_operation(message: types.Message, state: FSMContext):
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
async def eur_operation(message: types.Message, state: FSMContext):
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
# ___________________________________________________________________________________________________________________

# ___________________________________________________________________________________________________________________
@router.message(Command("update_operation"))
async def update_operation(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    connection = await connect_to_db()
    result = await connection.fetchval("SELECT * FROM users WHERE id = $1", user_id)

    if not result:
        await message.answer("Тебе нужно зарегистрироваться!")
        await state.clear()
    else:
        await message.answer("Введи идентификатор операции")
        await state.set_state(StatesBot.operationIdentifier)
    await connection.close()

@router.message(StateFilter(StatesBot.operationIdentifier))
async def operationIdentifier(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    try:
        operationIdentifier = int(message.text.strip())
        connection = await connect_to_db()
        result = await connection.fetchval("SELECT * FROM operations WHERE id = $1 and chat_id=$2", operationIdentifier,
                                       user_id)
        await connection.close()

        if result:
            await message.answer('Введите сумму, на которую хотите заменить')
            await state.update_data(operationIdentifier=operationIdentifier)
            await state.set_state(StatesBot.replacementAmount)
        else:
            await message.answer('Что-то пошло не так. Проверьте ваш индификатор.')
    except:
        await message.answer('Введено не коректное число.')


@router.message(StateFilter(StatesBot.replacementAmount))
async def replacementAmount(message: types.Message, state: FSMContext):
    try:
        replacementAmount = float(message.text.strip())

        data = await state.get_data()
        operationIdentifier = data.get('operationIdentifier')
        try:
            connection = await connect_to_db()
            result = await connection.fetchval("UPDATE operations SET sum=$1 WHERE id=$2",
                                               replacementAmount,
                                               operationIdentifier)
            await message.answer('Изменения успешно сохранены')
            await connection.close()
            await state.clear()
        except:
            await message.answer('Что-то пошло не так...')
    except:
        await message.answer('Вы ввели не коректное число')
# ___________________________________________________________________________________________________________________
async def main():
    await bot.set_my_commands(comands, scope=BotCommandScopeDefault())

    await dp.start_polling(bot)


asyncio.run(main())