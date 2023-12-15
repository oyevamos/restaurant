import psycopg2
import random

conn = psycopg2.connect(dbname="restaurant_bot_test", user="postgres", password="12345", host="localhost")
cur = conn.cursor()


def get_all_users():
    cur.execute("SELECT tg_id FROM users")

    res = cur.fetchall()

    return res


# Функция проверки наличия пользователя в базе данных
def check_user(user_id, username):
    cur.execute(f"SELECT id FROM users WHERE tg_id = '{user_id}'")
    tg_id = cur.fetchone()

    if tg_id is not None:
        return 1

    else:
        try:
            add_new_user(user_id, username)
            return 1

        except Exception:
            return 0


# Функция, которая будет добавлять новых пользователей
def add_new_user(user_id, username):
    try:
        cur.execute("SELECT MAX(id) FROM users")
        max_id = cur.fetchone()

        if max_id[0] is not None:
            new_max_id = max_id[0] + 1
            cur.execute(f"INSERT INTO users (id, tg_id, username) VALUES ('{new_max_id}', '{user_id}', '{username}')")
            add_new_user_bonuses(new_max_id)
            add_new_user_forms(new_max_id)

        else:
            max_id = 0
            cur.execute(f"INSERT INTO users (id, tg_id, username) VALUES ('{max_id}', '{user_id}', '{username}')")
            add_new_user_bonuses(max_id)
            add_new_user_forms(max_id)

        conn.commit()

        return 1

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в функции add_new_user {e}")
        return 0


# Функция, которая будет добавлять новых пользователей в таблицу с бонусами
def add_new_user_bonuses(max_id):
    try:
        cur.execute(f"INSERT INTO users_bonuses (id) VALUES ('{max_id}')")

        conn.commit()

        return 1

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в функции add_new_user_bonuses {e}")

        return 0


# Функция, которая будет добавлять новых пользователей в таблицу с информацией о пользователе
def add_new_user_forms(max_id):
    try:
        cur.execute(f"INSERT INTO users_forms (id) VALUES ('{max_id}')")

        conn.commit()

        return 1

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в функции add_new_user_forms {e}")

        return 0


def test_start_branch():
    """
    Тест ветки добавления пользователя в базу данных
    :return:
    1
    """
    for i in range(1, 101):
        num = random.randint(1000000, 10000000)
        assert check_user(num, f'test{i-1}') == 1


# Функция для добавления кода в бд
def add_personal_code(user_id, code):
    try:
        cur.execute(f"SELECT id FROM users WHERE tg_id = '{user_id}'")
        db_id = cur.fetchone()

        cur.execute(f"UPDATE users_bonuses SET personal_code = '{code}' WHERE id = '{db_id[0]}'")
        conn.commit()

        return 1

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в функции add_personal_code {e}")

        return 0


def test_personal_code():
    """
    Тест обновления персонального кода у пользователей
    :return:
    1
    """
    all_users = get_all_users()
    for i in all_users:
        num = random.randint(10000, 99999)
        assert add_personal_code(i[0], num) == 1


# Функция для добавления ФИО в бд
def update_fullname(user_id, fullname):
    try:
        cur.execute(f"SELECT id FROM users WHERE tg_id = '{user_id}'")
        db_id = cur.fetchone()

        cur.execute(f"UPDATE users_forms SET fullname = '{fullname}' WHERE id = '{db_id[0]}'")
        conn.commit()

        return 1

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в функции update_fullname {e}")

        return 0


# Функция для добавления даты рождения в бд
def update_date_of_birth(user_id, date_of_birth):
    try:
        cur.execute(f"SELECT id FROM users WHERE tg_id = '{user_id}'")
        db_id = cur.fetchone()

        cur.execute(f"UPDATE users_forms SET date_of_birth = '{date_of_birth}' WHERE id = '{db_id[0]}'")
        conn.commit()

        return 1

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в функции update_date_of_birth {e}")

        return 0


# Функция для добавления номера телефона в бд
def update_phone_number(user_id, phone_number):
    try:
        cur.execute(f"SELECT id FROM users WHERE tg_id = '{user_id}'")
        db_id = cur.fetchone()

        cur.execute(f"UPDATE users_forms SET phone_number = '{phone_number}' WHERE id = '{db_id[0]}'")
        conn.commit()

        return 1

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в функции update_phone_number {e}")

        return 0


def test_update_users_forms():
    """
    Тест для заполнения данных о пользователе
    :return:
    1
    """
    all_users = get_all_users()
    for i in all_users:
        literal = "абвгдеёжзийклмнопрстуфхцчшщЪыьэюяabcdefghijklmnopqrstuvwxyz"
        fullname = ""
        for j in range(0, 14):
            num = random.randint(0, len(literal) - 1)
            fullname += literal[num]
            if j % 7 == 0:
                fullname += " "
        assert update_fullname(i[0], fullname) == 1

        assert update_date_of_birth(i[0], f"{random.randint(1, 28)}.{random.randint(1, 12)}"
                                          f".{random.randint(1980, 2012)}.") == 1
        assert update_phone_number(i[0], random.randint(89000000000, 89999999999)) == 1


def truncate_table():
    try:
        cur.execute("TRUNCATE users;"
                    "TRUNCATE users_forms;"
                    "TRUNCATE users_bonuses;"
                    "TRUNCATE personal;"
                    "TRUNCATE waiters_info;"
                    "TRUNCATE bonus_history")
        conn.commit()

        return 1

    except Exception as e:
        conn.rollback()

        return 0


# def test_truncate_tables():
#     """
#     Тест отчистки всех таблиц
#     :return:
#     1
#     """
#     assert truncate_table() == 1
