import sqlite3


def create_db():
    conn = sqlite3.connect("user_memory.db")  # Имя файла базы данных
    cursor = conn.cursor()

    # Создание таблицы для пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            preferences TEXT DEFAULT '',
            facts TEXT DEFAULT '',
            places TEXT DEFAULT '',
            last_location TEXT DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()
    print("База данных успешно создана!")


if __name__ == "__main__":
    create_db()
