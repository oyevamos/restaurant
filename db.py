import psycopg2

conn = psycopg2.connect(dbname="restaurant_bot", user="postgres", password="12345", host="localhost")
cur = conn.cursor()


async def check_user(user_id, username):
    """
    Функция для проверки наличия пользователя в базе данных.

    Функция принимает на вход id пользователя в телеграмме, затем, проверяет присутствие данного id в
    базе данных users, если нет, тогда добавляем его с помощью функции add_new_user.

    :param user_id: id пользователя.
    :type user_id: int
    :param username: Имя пользователя.
    :type username: str
    :return: Результат функции.
    :rtype: bool
    """
    cur.execute(f"SELECT id FROM users WHERE tg_id = '{user_id}'")
    tg_id = cur.fetchone()

    if tg_id is not None:
        return True

    else:
        await add_new_user(user_id, username)
        return False


async def add_new_user(user_id, username):
    """
    Функция для добавления нового пользователя.

    Функция принимает на вход id пользователя в телеграмме и username, добавляет его в таблицу users посредством
    присваивания уникального идентификатора, равного максимальному существующему + 1.

    Если пользователь первый, кто зарегистрировался в боте, присваиваем ему 0 id.

    Также добавляем пользователя в таблицу с бонусами (add_new_user_bonuses) и
    в таблицу с личными данными (add_new_user_forms).

    :param user_id: id пользователя.
    :type user_id: int
    :param username: Имя пользователя.
    :type username: str
    :return: Результаты функции.
    :rtype: bool
    """
    try:
        cur.execute("SELECT MAX(id) FROM users")
        max_id = cur.fetchone()

        if max_id[0] is not None:
            new_max_id = max_id[0] + 1
            cur.execute(f"INSERT INTO users (id, tg_id, username) VALUES ('{new_max_id}', '{user_id}', '{username}')")
            await add_new_user_bonuses(new_max_id)
            await add_new_user_forms(new_max_id)

        else:
            max_id = 0
            cur.execute(f"INSERT INTO users (id, tg_id, username) VALUES ('{max_id}', '{user_id}', '{username}')")
            await add_new_user_bonuses(max_id)
            await add_new_user_forms(max_id)

        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в функции add_new_user {e}")


async def add_new_user_bonuses(max_id):
    """
    Функция, которая будет добавлять новых пользователей в таблицу с бонусами.

    Функция принимает на вход присвоенный уникальный id (max_id) и добавляем в таблицу users_bonuses.

    :param max_id: Уникальный id пользователя.
    :type max_id: int
    :return: Результат функции.
    :rtype: None
    """
    try:
        cur.execute(f"INSERT INTO users_bonuses (id) VALUES ('{max_id}')")

        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в функции add_new_user_bonuses {e}")


async def add_new_user_forms(max_id):
    """
    Функция, которая будет добавлять новых пользователей в таблицу с информацией о пользователе.

    Функция принимает на вход присвоенный уникальный id (max_id) и добавляем в таблицу users_forms.

    :param max_id: Уникальный id пользователя.
    :type max_id: int
    :return: Результат функции.
    :rtype: None
    """
    try:
        cur.execute(f"INSERT INTO users_forms (id) VALUES ('{max_id}')")

        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в функции add_new_user_forms {e}")


async def add_personal_code(user_id, code):
    """
    Функция, которая будет добавлять новых пользователей в таблицу с информацией о пользователе.

    Функция принимает на вход id пользователя в телеграмме (user_id)
    далее находит его идентификатор в таблице users, после чего записывает выданный персональный код в
    столбец personal_code.

    :param user_id: id пользователя в телеграмме.
    :type user_id: int
    :param code: Персональный 5-значный код.
    :type code: int
    :return: Результат функции.
    :rtype: None
    """
    try:
        cur.execute(f"SELECT id FROM users WHERE tg_id = '{user_id}'")
        db_id = cur.fetchone()

        cur.execute(f"UPDATE users_bonuses SET personal_code = '{code}' WHERE id = '{db_id[0]}'")
        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в функции add_personal_code {e}")


async def update_fullname(user_id, fullname):
    """
    Функция для добавления ФИО в бд.

    Функция принимает на вход id пользователя в телеграмме (user_id)
    далее находит его идентификатор в таблице users, после чего записывает введённое ФИО в
    столбец fullname.

    :param user_id: id пользователя в телеграмме.
    :type user_id: int
    :param fullname: Введённое ФИО.
    :type fullname: str
    :return: Результат функции.
    :rtype: None
    """
    try:
        cur.execute(f"SELECT id FROM users WHERE tg_id = '{user_id}'")
        db_id = cur.fetchone()

        cur.execute(f"UPDATE users_forms SET fullname = '{fullname}' WHERE id = '{db_id[0]}'")
        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в функции update_fullname {e}")


async def update_date_of_birth(user_id, date_of_birth):
    """
    Функция для добавления даты рождения в бд.

    Функция принимает на вход id пользователя в телеграмме (user_id)
    далее находит его идентификатор в таблице users, после чего записывает введённую дату рождения в
    столбец date_of_birth.

    :param user_id: id пользователя в телеграмме.
    :type user_id: int
    :param date_of_birth: Введённая дата рождения.
    :type date_of_birth: date
    :return: Результат функции.
    :rtype: None
    """
    try:
        cur.execute(f"SELECT id FROM users WHERE tg_id = '{user_id}'")
        db_id = cur.fetchone()

        cur.execute(f"UPDATE users_forms SET date_of_birth = '{date_of_birth}' WHERE id = '{db_id[0]}'")
        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в функции update_date_of_birth {e}")


async def update_phone_number(user_id, phone_number):
    """
    Функция для добавления номера телефона в базу данных.

    Функция принимает на вход id пользователя в телеграмме (user_id)
    далее находит его идентификатор в таблице users, после чего записывает введённый номер телефона в
    столбец phone_number.

    :param user_id: id пользователя в телеграмме.
    :type user_id: int
    :param phone_number: Введённый номер телефона.
    :type phone_number: str
    :return: Результат функции.
    :rtype: None
    """
    try:
        cur.execute(f"SELECT id FROM users WHERE tg_id = '{user_id}'")
        db_id = cur.fetchone()

        cur.execute(f"UPDATE users_forms SET phone_number = '{phone_number}' WHERE id = '{db_id[0]}'")
        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в функции update_phone_number {e}")


async def add_new_user_to_personal(user_id, role, username=None):
    """
    Функция, которая будет добавлять новых пользователей в таблицу с персоналом.

    Функция принимает на вход id пользователя в телеграмме (user_id) или username
    далее находит его идентификатор в таблице users, после чего вставляет в таблицу
    personal полученный id и выданную роль (role).

    :param user_id: id пользователя в телеграмме.
    :type user_id: int
    :param role: Выданная пользователю роль.
    :type role: str
    :param username:
    :return: Результат функции.
    :rtype: None
    """
    try:
        if username is None:
            cur.execute(f"SELECT id FROM users WHERE tg_id = '{user_id}'")
            db_id = cur.fetchone()

        else:
            cur.execute(f"SELECT id FROM users WHERE username = '{username}'")
            db_id = cur.fetchone()

        cur.execute(f"INSERT INTO personal (id, role) VALUES ('{db_id[0]}', '{role}')")

        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в функции add_new_user_to_personal {e}")


async def check_user_in_personal_table(user_id):
    """
    Функция, которая будет проверять наличие пользователя в таблице personal.

    Функция принимает на вход id пользователя в телеграмме (user_id)
    далее находит его идентификатор в таблице users, в случае присутствия такого идентификатора
    в таблице personal возвращаем его роль, при отсутствии возвращаем False.

    :param user_id: id пользователя в телеграмме.
    :type user_id: int
    :return: Результат функции.
    :rtype: str or bool
    """
    try:
        cur.execute(f"SELECT id FROM users WHERE tg_id = '{user_id}'")
        db_id = cur.fetchone()

        cur.execute(f"SELECT role FROM personal WHERE id = '{db_id[0]}'")
        role = cur.fetchone()

        if role is None:
            return False

        return role[0]

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в функции check_user_in_personal_table {e}")


async def check_username_in_users(username):
    """
    Функция проверки наличия username в таблице users.

    Функция принимает на вход username пользователя в телеграмме (username)
    далее ищет все строки, в которых присутствует его username, при их обнаружении возвращается 1,
    в противном случае возвращаем 0.

    :param username: username пользователя в телеграмме.
    :type username: str
    :return: Результат функции.
    :rtype: int
    """
    cur.execute(f"SELECT * FROM users WHERE username = '{username}'")
    res = cur.fetchone()

    if res is not None:
        return 1
    else:
        return 0


async def get_stats():
    """
    Функция для получения статистики.

    Возвращает все данные из таблиц users, users_forms, personal для дальнейшей отправки разработчику.

    :return: Результат функции.
    :rtype: tuple
    """
    cur.execute(f"SELECT * FROM users")
    users = cur.fetchall()

    cur.execute(f"SELECT * FROM users_forms")
    users_forms = cur.fetchall()

    cur.execute(f"SELECT * FROM personal")
    roles = cur.fetchall()

    return users, users_forms, roles


async def add_user_to_waiter_table(username):
    """
    Функция для добавления пользователя в таблицу официантов.

    Функция принимает на вход username пользователя в телеграмме (username)
    далее получает его уникальный id и добавляет в таблицу waiters_info, хранящую в себе все данные об официантах.

    :param username: username пользователя в телеграмме.
    :type username: str
    :return: Результат функции.
    :rtype: None
    """
    try:
        cur.execute(f"SELECT id FROM users WHERE username = '{username}'")
        db_id = cur.fetchone()[0]

        cur.execute(f"INSERT INTO waiters_info (id) VALUES ('{db_id}')")
        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в add_user_to_waiter_table {e}")


async def update_last_user_code(user_id, code):
    """
    Функция для обновления кода пользователя в таблице официантов.

    Функция принимает на вход id пользователя в телеграмме (user_id)
    далее получает его уникальный id и обновляет ячейку, хранящую в себе последний
    обслуженный код пользователя (last_user_code) на введённый.

    :param user_id: id пользователя в телеграмме.
    :type user_id: int
    :param code: Введённый персональный код.
    :type code: int
    :return: Результат функции.
    :rtype: None
    """
    try:
        cur.execute(f"SELECT id FROM users WHERE tg_id = '{user_id}'")
        db_id = cur.fetchone()[0]

        cur.execute(f"UPDATE waiters_info SET last_user_code = '{code}' WHERE id = '{db_id}'")
        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в update_last_user_code {e}")


async def get_last_user_code(user_id):
    """
    Функция для получения последнего кода пользователя у официанта.

    Функция принимает на вход id пользователя в телеграмме (user_id)
    далее получает его уникальный id и получает запись из ячейки, хранящую в себе последний
    обслуженный код пользователя (last_user_code) и возвращает его.

    :param user_id: id пользователя в телеграмме.
    :type user_id: int
    :return: Результат функции.
    :rtype: int
    """
    try:
        cur.execute(f"SELECT id FROM users WHERE tg_id = '{user_id}'")
        db_id = cur.fetchone()[0]

        cur.execute(f"SELECT last_user_code FROM waiters_info WHERE id = '{db_id}'")
        code = cur.fetchone()[0]

        return code

    except Exception as e:
        print(f"Ошибка в get_last_user_code {e}")


async def update_bonus_count(user_id, code, order_amount, request_type):
    """
    Функция для работы с бонусами.

    Функция принимает на вход id пользователя в телеграмме (user_id)
    далее получает его уникальный id, также персональный код пользователя (code),
    сумму заказа (order_amount) и тип работы с баллами (request_type).

    Если официант хочет списать баллы, тогда получаем текущий баланс пользователя по введённому коду и
    вычитаем из него 50% от суммы заказа, если новое кол-во баллов меньше 0, тогда присваиваем пользователю 0 баллов.

    Если официант хочет зачислить баллы, тогда получаем текущий баланс пользователя по введённому коду и
    прибавляем к нему 20% от суммы заказа.

    Возвращаем новый баланс пользователя и сумму заказа.

    :param user_id: id пользователя в телеграмме.
    :type user_id: int
    :param code: Введённый персональный код.
    :type code: int
    :param order_amount: Сумма заказа.
    :type order_amount: int
    :param request_type: Тип работы с баллами.
    :type request_type: str
    :return: Результат функции.
    :rtype: tuple
    """
    try:
        cur.execute(f"SELECT id FROM users WHERE tg_id = '{user_id}'")
        db_id = cur.fetchone()[0]

        cur.execute(f"UPDATE waiters_info SET customers_count = customers_count + 1 WHERE id = '{db_id}'")
        conn.commit()

        if request_type == "Списать":
            cur.execute(f"SELECT bonus_count FROM users_bonuses WHERE personal_code = '{code}'")
            balance = int(cur.fetchone()[0])
            if balance < int(order_amount) // 2:
                cur.execute(f"UPDATE users_bonuses SET bonus_count = '{0}' WHERE personal_code = '{code}'")
                conn.commit()

                return 0, int(order_amount) - balance

            else:
                cur.execute(f"UPDATE users_bonuses SET bonus_count = '{balance - int(order_amount) // 2}' "
                            f"WHERE personal_code = '{code}'")
                conn.commit()

                return balance - int(order_amount) // 2, int(order_amount) // 2

        elif request_type == "Зачислить":
            cur.execute(f"SELECT bonus_count FROM users_bonuses WHERE personal_code = '{code}'")
            balance = int(cur.fetchone()[0])

            cur.execute(f"UPDATE users_bonuses SET bonus_count = bonus_count + '{int(order_amount) // 5}'"
                        f" WHERE personal_code = '{code}'")
            conn.commit()

            return int(balance) + int(order_amount) // 5, order_amount

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в update_bonus_count {e}")


async def get_user_balance(user_id):
    """
    Функция получающая текущий бонусный баланс пользователя.

    Функция принимает на вход id пользователя в телеграмме (user_id)
    далее получает его уникальный id и получает запись из ячейки, хранящую в себе
    текущий бонусный баланс пользователя и возвращает его.

    :param user_id: id пользователя в телеграмме.
    :type user_id: int
    :return: Результат функции.
    :rtype: int
    """
    cur.execute(f"SELECT id FROM users WHERE tg_id = '{user_id}'")
    db_id = cur.fetchone()[0]

    cur.execute(f"SELECT bonus_count FROM users_bonuses WHERE id = '{db_id}'")
    cur_balance = cur.fetchone()[0]

    return cur_balance


async def update_register_user(user_id, code):
    """
    Функция для сохранения всех зарегистрированных пользователей.

    Функция принимает на вход id официанта в телеграмме (user_id) и
    персональный код пользователя (code), далее проверяем, что персональный
    id пользователя с введённым кодом ещё не был зарегистрирован официантом, в противном случае,
    возвращаем строку "Пользователь с таким персональным кодом уже зарегистрирован", также проверяем,
    что пользователь с таким идентификатором присутствует в базе дынных, в противном случае возвращаем,
    "Пользователя с таким персональным кодом не существует", после прохождения обеих проверок увеличиваем
    текущее значение ячейки inviting_users на 1, и в массив хранящийся в ячейке registers_users, добавляем
    уникальный id пользователя.

    :param user_id: id пользователя в телеграмме.
    :type user_id: int
    :param code: Персональный код.
    :type code: int
    :return: Результат функции.
    :rtype: str or bool
    """
    try:
        cur.execute(f"SELECT id FROM users_bonuses WHERE personal_code = {code}")
        db_user_id = cur.fetchone()

        cur.execute(f"SELECT id FROM users WHERE tg_id = {user_id}")
        db_waiter_id = cur.fetchone()

        if db_user_id is not None:
            cur.execute("SELECT registers_users FROM waiters_info")
            all_registers_users = cur.fetchall()

            if all_registers_users[0][0] is not None:
                for i in all_registers_users:
                    if str(db_user_id[0]) in i[0]:
                        return "Пользователь с таким персональным кодом уже зарегистрирован"

            cur.execute(f"SELECT registers_users FROM waiters_info WHERE id = {db_waiter_id[0]}")
            cur_users = cur.fetchone()

            if cur_users is not None:
                cur.execute(f"UPDATE waiters_info SET "
                            f"registers_users = array_append(registers_users, '{db_user_id[0]}'), "
                            f"inviting_users = inviting_users + 1 WHERE id = {db_waiter_id[0]}")
                conn.commit()

            else:
                cur.execute(f"UPDATE waiters_info SET "
                            f"registers_users = ARRAY{db_user_id[0]}, "
                            f"inviting_users = inviting_users + 1 WHERE id = {db_waiter_id[0]}")
                conn.commit()

            return 1

        else:
            return "Пользователя с таким персональным кодом не существует"

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в update_register_user {e}")


async def get_all_about_waiters():
    """
    Функция получающая все данные из таблицы waiters_info.

    Возвращает все строки из таблицы waiters_info и users_forms.

    :return: Результат функции.
    :rtype: tuple
    """
    cur.execute("SELECT * FROM waiters_info")
    res = cur.fetchall()

    cur.execute(f"SELECT * FROM users_forms")
    users_forms = cur.fetchall()

    return res, users_forms


async def get_username_by_db_id(db_id):
    """
    Функция для получения username по db_id.

    Функция принимает на вход id пользователя из таблицы users (db_id), и возвращает его username.

    :param db_id: id пользователя из таблицы users.
    :type db_id: int
    :return: Результат функции.
    :rtype: str
    """
    cur.execute(f"SELECT username FROM users WHERE id = '{db_id}'")
    username = cur.fetchone()

    return username[0]


async def add_operation_to_bonus_history(waiter_id, visitor_code, bonus_count, operation_date, operation_type):
    """
    Функция, которая будет записывать все операции с бонусами в таблицу.

    Функция принимает на вход id официанта в телеграмме (waiter_id), код посетителя (visitor_code),
    количество бонусов (bonus_count), дату операции (operation_date) и тип операции (operation_type).

    После обнаружения уникальных id официанта и посетителя из таблицы users записываем новую строку в
    таблицу bonus_history, где значения хранятся в таком же порядке.

    :param waiter_id: id официанта в телеграмме.
    :type waiter_id: int
    :param visitor_code: Код посетителя.
    :type visitor_code: int
    :param bonus_count: Количество бонусов.
    :type bonus_count: int
    :param operation_date: Дата операции.
    :type operation_date: date
    :param operation_type: Тип операции.
    :type operation_type: str
    :return: Результат функции.
    :rtype: None
    """
    try:
        cur.execute(f"SELECT id FROM users WHERE tg_id = {waiter_id}")
        db_waiter_id = cur.fetchone()

        cur.execute(f"SELECT id FROM users_bonuses WHERE personal_code = {visitor_code}")
        db_user_id = cur.fetchone()

        cur.execute("SELECT MAX(id) FROM bonus_history")
        max_id = cur.fetchone()

        if max_id[0] is not None:
            max_id = max_id[0] + 1

        else:
            max_id = 0

        cur.execute(f"INSERT INTO bonus_history "
                    f"(id, waiter_id, visitor_id, bonus_count, operation_date, operation_type) VALUES "
                    f"('{max_id}', '{db_waiter_id[0]}', '{db_user_id[0]}', '{bonus_count}',"
                    f" '{operation_date}', '{operation_type}')")

        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в add_operation_to_bonus_history {e}")


async def get_all_bonus_history():
    """
    Функция, которая будет получать всю историю баллов.

    Возвращает все строки из таблицы bonus_history.

    :return: Результат функции.
    :rtype: list
    """
    cur.execute("SELECT * FROM bonus_history")
    res = cur.fetchall()

    return res
