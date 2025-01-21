import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from crud_functions import initiate_db, get_all_products, populate_db

API_TOKEN = ''

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

initiate_db()
populate_db()


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()
    gender = State()


keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
button_calculate = KeyboardButton('Рассчитать')
button_info = KeyboardButton('Информация')
button_buy = KeyboardButton('Купить')
keyboard.add(button_calculate, button_info, button_buy)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    with open('imagenes/picture1.jpg', 'rb') as photo:
        await message.answer_photo(photo=photo, caption='Привет! Я бот, помогающий '
                                                        'твоему здоровью.\nВыберите действие:', reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == 'Информация')
async def send_info(message: types.Message):
    info_text = (
        "Этот бот поможет вам рассчитать вашу норму калорий на основе ваших параметров.\n"
        "Введите ваш пол, возраст, рост и вес, и бот предоставит вам информацию о вашей норме калорий.\n"
        "Нажмите 'Рассчитать', чтобы начать!"
    )
    await message.answer(info_text)


@dp.message_handler(lambda message: message.text == 'Купить')
async def get_buying_list(message: types.Message):
    products = get_all_products()
    if products:
        for product in products:
            await message.answer(
                f'Название: {product[1]} | Описание: {product[2]} | Цена: {product[3]}₽'
            )
            image_path = f'imagenes/picture{product[0] + 1}.jpg'
            try:
                with open(image_path, 'rb') as img:
                    await message.answer_photo(img)
            except FileNotFoundError:
                await message.answer("Изображение не найдено.")

        inline_keyboard = InlineKeyboardMarkup(row_width=2)
        for product in products:
            button = InlineKeyboardButton(product[1], callback_data=f'buy_{product[1]}')
            inline_keyboard.add(button)

        await message.answer('Выберете продукт для покупки:', reply_markup=inline_keyboard)
    else:
        await message.answer("Список продуктов пуст.")

@dp.callback_query_handler(lambda call: call.data.startswith('buy_'))
async def send_confirm_message(call: types.CallbackQuery):
    product_id = call.data.split('_', 1)[1]
    await call.message.answer(f'Вы успешно приобрели продукт с ID: {product_id}!')


@dp.message_handler(lambda message: message.text == 'Рассчитать')
async def mein_menu(message: types.Message):
    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    button_calories = InlineKeyboardButton('Рассчитать норму калорий', callback_data='calories')
    button_formulas = InlineKeyboardButton('Формулы расчёта', callback_data='formulas')
    inline_keyboard.add(button_calories, button_formulas)

    await message.answer('Выберите опцию:', reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda call: call.data == 'formulas')
async def get_formulas(call: types.CallbackQuery):
    formulas_text = (
        "Формула Миффлина-Сан Жеора:\n"
        "Для мужчин: BMR = 10 * вес(кг) + 6.25 * рост(см) - 5 * возраст(лет) + 5\n"
        "Для женщин: BMR = 10 * вес(кг) + 6.25 * рост(см) - 5 * возраст(лет) - 161"
    )
    await call.message.answer(formulas_text)


@dp.callback_query_handler(lambda call: call.data == 'calories')
async def set_gender(call: types.CallbackQuery):
    await UserState.gender.set()
    await call.message.answer('Введите ваш пол (мужчина/женщина):')


@dp.message_handler(state=UserState.gender)
async def set_age(message: types.Message, state: FSMContext):
    gender = message.text.lower()
    if gender in ['мужчина', 'женщина']:
        await state.update_data(gender=gender)
        await UserState.age.set()
        await message.answer('Введите свой возраст:')
    else:
        await message.answer('Пожалуйста, введите корректный пол (мужчина/женщина).')


@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(age=message.text)
        await UserState.growth.set()
        await message.answer('Введите свой рост (в см):')
    else:
        await message.answer('Пожалуйста, введите корректный возраст (число).')


@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(growth=message.text)
        await UserState.weight.set()
        await message.answer('Введите свой вес (в кг):')
    else:
        await message.answer('Пожалуйста, введите корректный рост (число).')


@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(weight=message.text)
        data = await state.get_data()

        if 'gender' in data and 'age' in data and 'growth' in data and 'weight' in data:
            gender = data['gender']
            age = int(data['age'])
            growth = int(data['growth'])
            weight = int(data['weight'])

            if gender == 'мужчина':
                calories = 66.5 + (13.75 * weight) + (5.003 * growth) - (6.75 * age)
            elif gender == 'женщина':
                calories = 655.1 + (9.563 * weight) + (1.850 * growth) - (4.676 * age)
            else:
                await message.answer('Ошибка: некорректный пол.')
                return

            await message.answer(f'Ваша норма калорий: {calories:.2f} ккал.')
        else:
            await message.answer('Ошибка: недостающие данные для расчета калорий.')

        await state.finish()
    else:
        await message.answer('Пожалуйста, введите корректный вес (число).')


@dp.message_handler(lambda message: True)
async def all_messages(message: types.Message):
    await message.answer('Введите команду /start, чтобы начать общение.')

if __name__ == '__main__':
    print('Бот запущен. Ожидание сообщений...')
    executor.start_polling(dp, skip_updates=True)
