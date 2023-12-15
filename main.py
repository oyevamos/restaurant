import random
import datetime

from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

import db

storage = MemoryStorage()


main_menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(KeyboardButton("Меню"),
                                                                   KeyboardButton("Контакты")).add(
    KeyboardButton("Персональный код"))  # Основная клавиатура

main_menu_for_developer_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Добавить официанта")).add(KeyboardButton("Добавить администратора")).row(
    KeyboardButton("Статистика"), KeyboardButton("История баллов")).row(KeyboardButton("Меню"),
                                                                        KeyboardButton("Контакты")).row(
    KeyboardButton("Персональный код"), KeyboardButton('Баланс'))

main_menu_for_admin_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Посмотреть статистику официантов")).add(KeyboardButton("История баллов")).row(
    KeyboardButton("Меню"), KeyboardButton("Контакты")).row(KeyboardButton("Персональный код"),
                                                            KeyboardButton('Баланс'))

main_menu_for_waiter_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(KeyboardButton("Зачислить"),
                                                                              KeyboardButton("Списать")).add(
    KeyboardButton("Зарегистрировать пользователя")).row(KeyboardButton("Меню"), KeyboardButton("Контакты")).row(
    KeyboardButton("Персональный код"), KeyboardButton('Баланс'))

back_button_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add("Назад")

show_menu_keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Меню",
                                                                     url="https://dodopizza.ru/"))  # Клавиатура с меню
show_contacts_keyboard = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text="Контакты", url="https://dodopizza.ru/moscow/contacts"))  # Клавиатура с меню


class Waiter(StatesGroup):
    enter_code_for_plus = State()
    plus_bonus = State()
    enter_code_for_minus = State()
    minus_bonus = State()
    register_user = State()


class Admin(StatesGroup):
    password = State()
    add_waiter = State()
    add_admin = State()


class Register(StatesGroup):
    fullname = State()
    date_of_birth = State()
    phone_number = State()


class MenuStates(StatesGroup):
    start = State()
    show_menu = State()
    contacts = State()
    code = State()


bot = Bot(token="6589343104:AAHYDuF9kUL7LA8fTFz2Tu4NR5jJ4fLLEU0")
dp = Dispatcher(bot, storage=storage)


# Обработка команды /start
@dp.message_handler(commands='start', state='*')
async def handle_start_command(message: types.Message, state: FSMContext):
    flag_exists = await db.check_user(message.from_user.id, message.from_user.username)
    await state.finish()  # Сбрасывает состояние пользователя до нуля

    if flag_exists:
        cur_role = await db.check_user_in_personal_table(message.from_user.id)
        print(cur_role)
        if not cur_role:
            await bot.send_message(message.from_user.id, "Добро пожаловать обратно", reply_markup=main_menu_keyboard)

        elif "Разработчик" in cur_role:

            await bot.send_message(message.from_user.id, "Добро пожаловать обратно, уважаемый разработчик",
                                   reply_markup=main_menu_for_developer_keyboard)

        elif "Администратор" in cur_role:

            await bot.send_message(message.from_user.id, "Добро пожаловать обратно, уважаемый админ",
                                   reply_markup=main_menu_for_admin_keyboard)

        elif "Официант" in cur_role:

            await bot.send_message(message.from_user.id, "Добро пожаловать обратно, подаван",
                                   reply_markup=main_menu_for_waiter_keyboard)

        await MenuStates.start.set()

    else:
        await bot.send_message(message.from_user.id, "Привет, рад видеть тебя тут впервые, отправь мне своё ФИО")
        await Register.fullname.set()


# Обработка команды /admin
@dp.message_handler(commands='admin', state='*')
async def handle_admin_command(message: types.Message):
    await bot.send_message(message.from_user.id, "Вы пытаетесь авторизоваться как администратор,"
                                                 " подтвердите свои права вводом пароля:")
    await Admin.password.set()


@dp.message_handler(state=Admin.password)
async def handle_admin_password(message: types.Message):
    if message.text == "12345":
        await bot.send_message(message.from_user.id, "Вы успешно подтвердили свои права, добавляю"
                                                     " расширенный функционал")
        await db.add_new_user_to_personal(message.from_user.id, "Разработчик")
    else:
        await bot.send_message(message.from_user.id, "Вы не прошли аутентификацию и были возвращены"
                                                     " в основное меню", reply_markup=main_menu_keyboard)
        await MenuStates.start.set()


@dp.message_handler(state=Register.fullname)
async def handle_fullname(message: types.Message):
    await bot.send_message(message.from_user.id,
                           f"{message.text} приятно познакомиться, теперь отправь мне дату рождения")
    await db.update_fullname(message.from_user.id, message.text)
    await Register.date_of_birth.set()


@dp.message_handler(state=Register.date_of_birth)
async def handle_dob(message: types.Message):
    separators = ['.']
    for separator in separators:
        try:
            dob = datetime.datetime.strptime(message.text, f"%d{separator}%m{separator}%Y")
            if dob.year > 1930:
                await bot.send_message(message.from_user.id, "Замечательно, теперь жду вашего номера телефона")
                await db.update_date_of_birth(message.from_user.id, dob)
                await Register.phone_number.set()

            else:
                await bot.send_message(message.from_user.id, f"Если вы действительно {dob.year} года рождения, "
                                                             f"предоставьте паспорт разработчику и мы это учтём")

        except ValueError:
            await bot.send_message(message.from_user.id, "Извините, я принимаю только даты следующего формата:"
                                                         "(ДД.ММ.ГГГГ)")


@dp.message_handler(state=Register.phone_number)
async def handle_phone_number(message: types.Message):
    if ((message.text[0] == "+" and message.text[1] == "7" and len(message.text) == 12) or
            (message.text[0] == "7" and len(message.text) == 11) or
            (message.text[0] == "8" and len(message.text) == 11)):
        await bot.send_message(message.from_user.id, "Регистрация прошла успешно\n"
                                                     "Вам зачислено 500 бонусов")

        await bot.send_message(message.from_user.id, "Теперь выберите любой пункт на"
                                                     " клавиатуре", reply_markup=main_menu_keyboard)
        await db.update_phone_number(message.from_user.id, message.text)
        await MenuStates.start.set()

    else:
        await bot.send_message(message.from_user.id, "Вы ввели некорректный номер телефона, следуйте"
                                                     " следующим форматам:\n"
                                                     "+7917xxxxxxx\n"
                                                     "7917xxxxxxx\n"
                                                     "8917xxxxxxx")


@dp.message_handler(state=MenuStates.start)
async def send_menu_to_user(message: types.Message):
    if message.text == "Меню":
        await bot.send_message(message.from_user.id, "Смотри наше меню", reply_markup=show_menu_keyboard)

    elif message.text == "Контакты":
        await bot.send_message(message.from_user.id, "Вот наши контакты", reply_markup=show_contacts_keyboard)

    elif message.text == "Персональный код":
        personal_code = random.randint(10000, 99999)
        await db.add_personal_code(message.from_user.id, personal_code)
        await bot.send_message(message.from_user.id, f"Ваш персональный код: {personal_code}")

    elif message.text == "Баланс":
        cur_balance = await db.get_user_balance(message.from_user.id)
        await bot.send_message(message.from_user.id, f"Ваш текущий баланс: {cur_balance} бонусов")

    elif message.text == "Добавить официанта":
        cur_role = await db.check_user_in_personal_table(message.from_user.id)
        if cur_role == "Разработчик":
            await bot.send_message(message.from_user.id, "Отправьте имя пользователя, которому вы хотите присвоить"
                                                         " роль 'Официант'")
            await Admin.add_waiter.set()

        else:
            await bot.send_message(message.from_user.id, "Извините, но у вас не достаточно прав доступа")

    elif message.text == "Добавить администратора":
        cur_role = await db.check_user_in_personal_table(message.from_user.id)
        if cur_role == "Разработчик":
            await bot.send_message(message.from_user.id, "Отправьте имя пользователя, которому вы хотите присвоить"
                                                         " роль 'Администратор'")
            await Admin.add_admin.set()

        else:
            await bot.send_message(message.from_user.id, "Извините, но у вас не достаточно прав доступа")

    elif message.text == "Статистика":
        cur_role = await db.check_user_in_personal_table(message.from_user.id)
        if cur_role == "Разработчик":
            all_users, all_users_forms, all_roles = await db.get_stats()
            msg = (f'Всего зарегистрировано пользователей: {len(all_users)}\n'
                   f'Всего пользователей с ролями: {len(all_roles)}\n'
                   f'----------------------\n')
            for i in all_users:
                for y in all_users_forms:
                    if i[0] == y[0]:
                        cur_role = await db.check_user_in_personal_table(i[1])

                        msg += (f"id: {i[0]}\n"
                                f"\nРоль: {cur_role}\n"
                                f"username: @{i[2]} ({i[1]})\n"
                                f"Имя: {y[1]}\n"
                                f"Дата рождения: {y[2]}\n"
                                f"Номер телефона: {y[3]}\n\n"
                                f"----------------------\n")
            await bot.send_message(message.from_user.id, "Статистика на текущий момент:\n" + msg)

        else:
            await bot.send_message(message.from_user.id, "Извините, но у вас не достаточно прав доступа")

    elif message.text == "История баллов":
        cur_role = await db.check_user_in_personal_table(message.from_user.id)
        if cur_role == "Администратор" or cur_role == "Разработчик":
            msg = ('История баллов:\n'
                   '----------------------\n')

            history = await db.get_all_bonus_history()
            for i in history:
                if i[5] == "Зачислить":
                    msg += (f'\nНомер в списке: {i[0]}\n'
                            f'Зачисление баллов от @{await db.get_username_by_db_id(i[1])}\n'
                            f'Кол-во: {i[3]} баллов\n'
                            f'Кому: @{await db.get_username_by_db_id(i[2])}\n'
                            f'Когда: {i[4]}\n\n'
                            f'----------------------\n')

                elif i[5] == "Списать":
                    msg += (f'\nНомер в списке: {i[0]}\n'
                            f'Списание баллов от @{await db.get_username_by_db_id(i[1])}\n'
                            f'Кол-во: {i[3]} баллов\n'
                            f'У кого: @{await db.get_username_by_db_id(i[2])}\n'
                            f'Когда: {i[4]}\n\n'
                            f'----------------------\n')

                else:
                    msg += f'\n{i[0]}: Произошла ошибка'

            await bot.send_message(message.from_user.id, msg)

        else:
            await bot.send_message(message.from_user.id, "Извините, но у вас не достаточно прав доступа")

    elif message.text == "Посмотреть статистику официантов":
        cur_role = await db.check_user_in_personal_table(message.from_user.id)
        if cur_role == "Администратор":
            all_about_waiters, info_about_users = await db.get_all_about_waiters()
            msg = ('Статистика официантов:\n'
                   '----------------------\n')

            for i in all_about_waiters:
                for y in info_about_users:
                    if i[0] == y[0]:

                        visitors_username = [f"@{await db.get_username_by_db_id(x)}" for x in i[4][0]]

                        msg += (f'\nИмя пользователя: @{await db.get_username_by_db_id(i[0])}\n'
                                f'Имя: {y[1]}\n'
                                f'Номер телефона: {y[3]}\n'
                                f'Кол-во принятых заказов: {i[1]}\n'
                                f'Кол-во зарегистрированных гостей: {i[2]} | {visitors_username}\n'
                                f'Последний обслуженный код пользователя: {i[3]}\n\n'
                                f'----------------------\n')

            await bot.send_message(message.from_user.id, msg)
            await bot.send_message(message.from_user.id, "Меню", reply_markup=main_menu_for_admin_keyboard)
        else:
            await bot.send_message(message.from_user.id, "Извините, но у вас не достаточно прав доступа")

    elif message.text == "Зачислить":
        cur_role = await db.check_user_in_personal_table(message.from_user.id)
        if cur_role == "Официант":
            await bot.send_message(message.from_user.id, "Отправьте код пользователя",
                                   reply_markup=back_button_keyboard)
            await Waiter.enter_code_for_plus.set()
        else:
            await bot.send_message(message.from_user.id, "Извините, но у вас не достаточно прав доступа")

    elif message.text == "Списать":
        cur_role = await db.check_user_in_personal_table(message.from_user.id)
        if cur_role == "Официант":
            await bot.send_message(message.from_user.id, "Отправьте код пользователя",
                                   reply_markup=back_button_keyboard)
            await Waiter.enter_code_for_minus.set()
        else:
            await bot.send_message(message.from_user.id, "Извините, но у вас не достаточно прав доступа")

    elif message.text == "Зарегистрировать пользователя":
        cur_role = await db.check_user_in_personal_table(message.from_user.id)
        if cur_role == "Официант":
            await bot.send_message(message.from_user.id, "Отправьте персональный код пользователя")
            await Waiter.register_user.set()

        else:
            await bot.send_message(message.from_user.id, "Извините, но у вас не достаточно прав доступа")

    else:
        await bot.send_message(message.from_user.id, "Извините, я вас не понимаю")


@dp.message_handler(state=Admin.add_waiter)
async def handle_add_waiter(message: types.Message):
    res = await db.check_username_in_users(message.text)
    if res:
        try:
            await db.add_new_user_to_personal(message.from_user.id, "Официант", message.text)
            await db.add_user_to_waiter_table(message.text)
            await bot.send_message(message.from_user.id, "Роль официанта успешно присвоена",
                                   reply_markup=main_menu_for_developer_keyboard)
            await MenuStates.start.set()

        except Exception as e:
            await bot.send_message(message.from_user.id, f"Что-то пошло не так\n"
                                                         f"{e}", reply_markup=main_menu_for_developer_keyboard)
            await MenuStates.start.set()

    else:
        await bot.send_message(message.from_user.id, "Извините, такого пользователя в базе данных нет",
                               reply_markup=main_menu_for_developer_keyboard)
        await MenuStates.start.set()


@dp.message_handler(state=Admin.add_admin)
async def handle_add_waiter(message: types.Message):
    res = await db.check_username_in_users(message.text)
    if res:
        try:
            await db.add_new_user_to_personal(message.from_user.id, "Администратор", message.text)
            await bot.send_message(message.from_user.id, "Роль администратора успешно присвоена",
                                   reply_markup=main_menu_for_developer_keyboard)
            await MenuStates.start.set()

        except Exception as e:
            await bot.send_message(message.from_user.id, f"Что-то пошло не так\n"
                                                         f"{e}", reply_markup=main_menu_for_developer_keyboard)
            await MenuStates.start.set()

    else:
        await bot.send_message(message.from_user.id, "Извините, такого пользователя в базе данных нет",
                               reply_markup=main_menu_for_developer_keyboard)
        await MenuStates.start.set()


@dp.message_handler(state=Waiter.enter_code_for_plus)
async def handle_code_for_plus(message: types.Message, state: FSMContext):
    try:
        if message.text != "Назад":
            int(message.text)
            async with state.proxy() as data:
                data["type"] = "Зачислить"
                data["code"] = message.text

            await db.update_last_user_code(message.from_user.id, message.text)
            await bot.send_message(message.from_user.id, "Отправьте сумму заказа пользователя",
                                   reply_markup=back_button_keyboard)
            await Waiter.plus_bonus.set()

        else:
            await bot.send_message(message.from_user.id, "Меню", reply_markup=main_menu_for_waiter_keyboard)
            await MenuStates.start.set()

    except ValueError:
        await bot.send_message(message.from_user.id, "Извините, но я принимаю только числа")


@dp.message_handler(state=Waiter.plus_bonus)
async def handle_bonus_count_for_plus(message: types.Message, state: FSMContext):
    try:
        if message.text != "Назад":
            int(message.text)
            code = await db.get_last_user_code(message.from_user.id)
            new_balance, order_amount = await db.update_bonus_count(message.from_user.id, code, message.text,
                                                                    "Зачислить")
            async with state.proxy() as data:
                data["bonus_count"] = int(message.text)//5
                visitor_code = data["code"]
                operation_type = data["type"]
                bonus_count = data["bonus_count"]

            await bot.send_message(message.from_user.id, f"Посетителю зачислено: {int(message.text)//5}\n"
                                                         f"Новый бонусный баланс: {new_balance}")

            await db.add_operation_to_bonus_history(message.from_user.id, visitor_code, bonus_count,
                                                    datetime.datetime.now(), operation_type)

            await state.reset_state()

            await bot.send_message(message.from_user.id, "Меню", reply_markup=main_menu_for_waiter_keyboard)
            await MenuStates.start.set()

        else:
            await bot.send_message(message.from_user.id, "Отправьте персональный код пользователя",
                                   reply_markup=back_button_keyboard)
            await Waiter.enter_code_for_plus.set()

    except ValueError:
        await bot.send_message(message.from_user.id, "Извините, но я принимаю только числа")


@dp.message_handler(state=Waiter.enter_code_for_minus)
async def handle_code_for_plus(message: types.Message, state: FSMContext):
    try:
        if message.text != "Назад":
            int(message.text)
            async with state.proxy() as data:
                data["type"] = "Списать"
                data["code"] = message.text
            await db.update_last_user_code(message.from_user.id, message.text)
            await bot.send_message(message.from_user.id, "Отправьте сумму заказа пользователя",
                                   reply_markup=back_button_keyboard)
            await Waiter.minus_bonus.set()

        else:
            await bot.send_message(message.from_user.id, 'Меню', reply_markup=main_menu_for_waiter_keyboard)
            await MenuStates.start.set()

    except ValueError:
        await bot.send_message(message.from_user.id, "Извините, но я принимаю только числа")


@dp.message_handler(state=Waiter.minus_bonus)
async def handle_bonus_count_for_minus(message: types.Message, state: FSMContext):
    try:
        if message.text != "Назад":
            int(message.text)

            code = await db.get_last_user_code(message.from_user.id)
            cur_balance, cur_order_amount = await db.update_bonus_count(message.from_user.id, code, message.text,
                                                                        "Списать")
            await bot.send_message(message.from_user.id, f"Оставшийся баланс пользователя: {cur_balance}\n"
                                                         f"Новая сумма заказа: {cur_order_amount}")

            async with state.proxy() as data:
                data["bonus_count"] = int(message.text) - cur_order_amount
                visitor_code = data["code"]
                operation_type = data["type"]
                bonus_count = data["bonus_count"]

            await db.add_operation_to_bonus_history(message.from_user.id, visitor_code, bonus_count,
                                                    datetime.datetime.now(), operation_type)

            await state.reset_state()

            await bot.send_message(message.from_user.id, "Меню", reply_markup=main_menu_for_waiter_keyboard)
            await MenuStates.start.set()

        else:
            await bot.send_message(message.from_user.id, "Отправьте персональный код посетителя",
                                   reply_markup=back_button_keyboard)
            await Waiter.enter_code_for_minus.set()

    except ValueError:
        await bot.send_message(message.from_user.id, "Извините, но я принимаю только числа")


@dp.message_handler(state=Waiter.register_user)
async def handle_register_user(message: types.Message):
    try:
        int(message.text)
        res = await db.update_register_user(message.from_user.id, message.text)

        if res == 1:
            await bot.send_message(message.from_user.id, "Регистрация пользователя прошла успешно")

        else:
            await bot.send_message(message.from_user.id, res)

        await bot.send_message(message.from_user.id, "Меню", reply_markup=main_menu_for_waiter_keyboard)
        await MenuStates.start.set()

    except ValueError:
        await bot.send_message(message.from_user.id, "Извините, но я принимаю только числа")


executor.start_polling(dp, skip_updates=True)
