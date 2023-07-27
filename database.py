import psycopg2
from psycopg2 import Error
from config import *

try:
    # Подключение к существующей базе данных
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )
    cursor = connection.cursor()
    # Выполнение SQL-запроса
    cursor.execute("SELECT version();")
    # Получить результат
    record = cursor.fetchone()
    print("Вы подключены к - ", record, "\n")
    cursor.close()
    connection.rollback()
except (Exception, Error) as error:
    print("Ошибка при работе с PostgreSQL", error)


connection.autocommit = True


def create_table_users():
    """СОЗДАНИЕ ТАБЛИЦЫ USERS (НАЙДЕННЫЕ ПОЛЬЗОВАТЕЛИ"""
    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS users(
                id serial,
                first_name varchar(50) NOT NULL,
                last_name varchar(25) NOT NULL,
                vk_id varchar(20) NOT NULL PRIMARY KEY,
                vk_link varchar(50));"""
        )
    print("[INFO] Table USERS was created.")


def create_table_seen_users():  # references users(vk_id)
    """СОЗДАНИЕ ТАБЛИЦЫ SEEN_USERS (ПРОСМОТРЕННЫЕ ПОЛЬЗОВАТЕЛИ"""
    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS seen_users(
            id serial,
            vk_id varchar(50) PRIMARY KEY,
            offset_user varchar(25) NOT NULL);"""
        )
    print("[INFO] Table SEEN_USERS was created.")


def insert_data_users(first_name, last_name, vk_id, vk_link):
    """ВСТАВКА ДАННЫХ В ТАБЛИЦУ USERS"""
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            INSERT INTO users (first_name, last_name, vk_id, vk_link) 
            VALUES ('{first_name}', '{last_name}', '{vk_id}', '{vk_link}')
            ON CONFLICT (vk_id)
            DO NOTHING;
            """
        )


def insert_data_seen_users(vk_id, offset_user):
    """ВСТАВКА ДАННЫХ В ТАБЛИЦУ SEEN_USERS"""
    with connection.cursor() as cursor:
        cursor.execute(
            f"""INSERT INTO seen_users (vk_id, offset_user) 
            VALUES ('{vk_id}', '{offset_user}')
            ON CONFLICT (vk_id)
            DO NOTHING;
            """
        )

def select(offset):
    """ВЫБОРКА ИЗ НЕПРОСМОТРЕННЫХ ЛЮДЕЙ"""
    with connection.cursor() as cursor:
        cursor.execute(
            f"""SELECT u.first_name,
                        u.last_name,
                        u.vk_id,
                        u.vk_link,
                        su.vk_id
                        FROM users AS u
                        LEFT JOIN seen_users AS su 
                        ON u.vk_id = su.vk_id
                        WHERE su.vk_id IS NULL
                        OFFSET '{offset}';"""
        )
        return cursor.fetchone()

def fetchall_user():
    with connection.cursor() as cursor:
        postgreSQL_select_Query = "select * from users"
        cursor.execute(postgreSQL_select_Query)
        mobile_records = cursor.fetchall()
    return mobile_records

def fetchall_seen_user():
    with connection.cursor() as cursor:
        postgreSQL_select_Query = "select * from seen_users"
        cursor.execute(postgreSQL_select_Query)
        mobile_records = cursor.fetchall()
    return mobile_records


def creating_database():
    create_table_users()
    create_table_seen_users()