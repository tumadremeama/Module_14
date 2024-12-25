from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import crud_functions2

API_TOKEN = ''

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


crud_functions2.initiate_db()


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()
    gender = State()


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()


keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
button_calculate = KeyboardButton('Рассчитать')
button_info = KeyboardButton('Информация')
button_buy = KeyboardButton('Купить')
keyboard.add(button_calculate, button_info, button_buy)


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer('Добро пожаловать в нашего бота! Выберите действие:\n'
                         '1. Напишите "Регистрация", чтобы зарегистрироваться.\n'
                         '2. Нажмите "Рассчитат", чтобы рассчитать калории\n'
                         '3. Нажмите "Информачию", чтобы узнать подробнее.\n'
                         '4. Нажмите "Купить", чтобы просмотреть продукты.\n')


@dp.message_handler(lambda message: message.text == 'Регистрация')
async def sing_up(message: types.Message):
    await message.answer('Введите имя пользователя (только латинский алфавит):')
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message: types.Message, state: FSMContext):
    username = message.text
    if username.isalpha():
        if crud_functions2.is_included(username):
            await message.answer('Пользователь существует, введите другое имя:')
            return
        await state.update_data(username=username)
        await message.answer('Введите свой email:')
        await RegistrationState.email.set()
    else:
        await message.answer('Имя пользователя должно содержать только латинские буквы. Попробуйте снова.')


@dp.message_handler(state=RegistrationState.email)
async def set_email(message: types.Message, state: FSMContext):
    email = message.text
    await state.update_data(email=email)
    await message.answer('Введите свой возраст:')
    await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message: types.Message, state: FSMContext):
    age = message.text
    data = await state.get_data()
    username = data.get('username')
    email = data.get('email')

    try:
        age = int(age)
        crud_functions2.add_user(username, email, age)
        await message.answer('Регистрация прошла успешно! Добро пожаловать!')
    except ValueError:
        await message.answer('Возраст должен быть числом. Попробуйте снова.')
        return

    await state.finish()


@dp.message_handler(lambda message: message.text == 'Купить')
async def get_buying_list(message: types.Message):
    products = [
        {'name': 'Vitamin C', 'description': 'Витамин ц, 60 кап. 900мг, зищита для иммунитета', 'price': 599, 'image':
            'imagenes/picture2.jpg'},

        {'name': 'Multi-One Vitamin', 'description': 'Мултивитаминный комплекс, 30 кап. пищевая добавка',
         'price': 1200, 'image': 'imagenes/picture3.jpg'},

        {'name': 'B-Complex Vitamin', 'description': 'Б-Витамин комплекс, от Б1 до Б12, для энергии и антистресса',
         'price': 956, 'image': 'imagenes/picture4.jpg'},

        {'name': 'Calcium, Magnesium w. V. D3', 'description': 'Способствует здоровью костей, '
                                                               'поддерживает функции нервов и мышц',
         'price': 1299, 'image': 'imagenes/picture5.jpg'},
    ]
    for product in products:
        await message.answer(
            f'Название: {product["name"]} | Описание: {product["description"]} | Цена: {product["price"]}₽'
        )
        with open(product['image'], 'rb') as img:
            await message.answer_photo(img)

    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    for product in products:
        button = InlineKeyboardButton(product['name'], callback_data=f'buy_{product["name"]}')
        inline_keyboard.add(button)

    await message.answer('Выберете продукт для покупки:', reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda call: call.data.startswith('buy_'))
async def send_confirm_message(call: types.CallbackQuery):
    product_name = call.data.split('_', 1)[1]
    await call.message.answer(f'Вы успешно приобрели продукт!')


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


@dp.message_handler(lambda message: message.text == 'Информация')
async def send_info(message: types.Message):
    info_text = (
            "Этот бот поможет вам рассчитать вашу норму калорий на основе ваших параметров.\n"
            "Введите ваш пол, возраст, рост и вес, и бот предоставит вам информацию о вашей норме калорий.\n"
            "Нажмите 'Рассчитать', чтобы начать!\n"
            "А так же информация о наших продуктах, чтобы узнать поподробнее нажмите 'Купить'"
        )
    await message.answer(info_text)


@dp.message_handler(lambda message: True)
async def all_messages(message: types.Message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == '__main__':
    print('Бот запущен. Ожидание сообщений...')
    executor.start_polling(dp, skip_updates=True)
