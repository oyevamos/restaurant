import psycopg2
import random

conn = psycopg2.connect(dbname="restaurant_bot_test", user="postgres", password="AiRa6779", host="localhost")
cur = conn.cursor()


# Функция для получения всех пользователей
def get_all_users():
    cur.execute("SELECT tg_id FROM users")

    res = cur.fetchall()

    return res


# Функция для получения username по id пользователя
def get_username_by_id(user_id):
    cur.execute(f"SELECT username FROM users WHERE tg_id = '{user_id}'")
    username = cur.fetchone()

    return username[0]


# Функция для получения всего персонала
def get_all_personal():
    cur.execute(f"SELECT id FROM personal WHERE role = '{'Официант'}'")
    all_personal = cur.fetchall()

    tg_ids = []
    for i in all_personal:
        cur.execute(f"SELECT tg_id FROM users WHERE id = '{i[0]}'")
        res = cur.fetchone()
        tg_ids.append(res)

    return tg_ids


# Функция получения персонального кода пользователя
def get_code_by_id(user_id):
    cur.execute(f"SELECT id FROM users WHERE tg_id = '{user_id[0]}'")
    db_id = cur.fetchone()

    cur.execute(f"SELECT personal_code FROM users_bonuses WHERE id = '{db_id[0]}'")
    code = cur.fetchone()[0]

    return code


def add_new_user_to_personal(user_id, role, username=None):
    try:
        if username is None:
            cur.execute(f"SELECT id FROM users WHERE tg_id = '{user_id}'")
            db_id = cur.fetchone()

        else:
            cur.execute(f"SELECT id FROM users WHERE username = '{username}'")
            db_id = cur.fetchone()

        cur.execute(f"INSERT INTO personal (id, role) VALUES ('{db_id[0]}', '{role}')")

        conn.commit()

        return 1

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в функции add_new_user_to_personal {e}")

        return 0


def add_user_to_waiter_table(username):
    try:
        cur.execute(f"SELECT id FROM users WHERE username = '{username}'")
        db_id = cur.fetchone()[0]

        cur.execute(f"INSERT INTO waiters_info (id) VALUES ('{db_id}')")
        conn.commit()

        return 1

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в add_user_to_waiter_table {e}")

        return 0


def test_new_user_in_personal():
    """
    Тест добавления нового пользователя в таблицу персонала
    :return:
    1
    """
    all_users = get_all_users()
    role = ["Официант", "Администратор", "Разработчик"]
    for i in all_users:
        role_str = role[random.randint(0, 2)]
        assert add_new_user_to_personal(i[0], role_str) == 1
        if role_str == "Официант":
            username = get_username_by_id(i[0])
            assert add_user_to_waiter_table(username) == 1


# Функция для обновления кода пользователя в таблице официантов
def update_last_user_code(user_id, code):
    try:
        cur.execute(f"SELECT id FROM users WHERE tg_id = '{user_id[0]}'")
        db_id = cur.fetchone()[0]

        cur.execute(f"UPDATE waiters_info SET last_user_code = '{code}' WHERE id = '{db_id}'")
        conn.commit()

        return 1

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в update_last_user_code {e}")

        return 0


def update_register_user(user_id, code):
    try:
        cur.execute(f"SELECT id FROM users_bonuses WHERE personal_code = {code}")
        db_user_id = cur.fetchone()

        cur.execute(f"SELECT id FROM users WHERE tg_id = {user_id[0]}")
        db_waiter_id = cur.fetchone()

        if db_user_id is not None:
            cur.execute("SELECT registers_users FROM waiters_info")
            all_registers_users = cur.fetchall()

            if all_registers_users[0][0] is not None:
                for i in all_registers_users:
                    if i[0] is not None:
                        if str(db_user_id[0]) in i[0]:
                            print("Пользователь с таким персональным кодом уже зарегистрирован")
                            return 1

            cur.execute(f"SELECT registers_users FROM waiters_info WHERE id = {db_waiter_id[0]}")
            cur_users = cur.fetchone()

            if cur_users is not None:
                cur.execute(f"UPDATE waiters_info SET "
                            f"registers_users = array_append(registers_users, '{db_user_id[0]}'), "
                            f"inviting_users = inviting_users + 1 WHERE id = {db_waiter_id[0]}")
                conn.commit()

            else:
                cur.execute(f"UPDATE waiters_info SET "
                            f"registers_users = '{db_user_id[0]}', "
                            f"inviting_users = inviting_users + 1 WHERE id = {db_waiter_id[0]}")
                conn.commit()

            return 1

        else:
            print("Пользователя с таким персональным кодом не существует")
            return 1

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в update_register_user {e}")

        return 0


def test_update_user_code_in_personal():
    """
    Тест обновления последнего обслуженного персонального кода гостя
    :return:
    1
    """

    all_personal = get_all_personal()
    for i in all_personal:
        code = random.randint(10000, 99999)
        assert update_last_user_code(i, code) == 1
        assert update_register_user(i, get_code_by_id(i)) == 1


def get_stats():
    try:
        cur.execute(f"SELECT * FROM users")
        users = cur.fetchall()

        cur.execute(f"SELECT * FROM users_forms")
        users_forms = cur.fetchall()

        cur.execute(f"SELECT * FROM personal")
        roles = cur.fetchall()

        print(users, users_forms, roles)

        return 1

    except Exception as e:
        return 0


def test_get_stats():
    """
    Тест получения статистики персонала
    :return:
    1
    """
    assert get_stats() == 1
