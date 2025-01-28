import sqlite3

DB_PATH = "user_memory.db"


def update_last_location(user_id, location):
    """
    Обновляет последнюю локацию пользователя.
    :param user_id: ID пользователя
    :param location: Последняя локация в формате строки (например, '55.7558,37.6173')
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO users (user_id, last_location)
    VALUES (?, ?)
    ON CONFLICT(user_id) DO UPDATE SET last_location = excluded.last_location
    ''', (user_id, location))

    conn.commit()
    conn.close()


def get_last_location(user_id):
    """
    Возвращает последнюю сохраненную локацию пользователя.
    :param user_id: ID пользователя
    :return: Последняя локация (строка) или None, если нет данных
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT last_location FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    conn.close()

    return result[0] if result else None


# Функция для сохранения предпочтений пользователя
def save_preference(user_id: int, preference: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Проверяем, существует ли пользователь
    cursor.execute("SELECT preferences FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if result:
        # Если пользователь существует, добавляем новое предпочтение
        current_preferences = result[0]
        new_preferences = f"{current_preferences} | {preference}".strip(" | ")
        cursor.execute("UPDATE users SET preferences = ? WHERE user_id = ?", (new_preferences, user_id))
    else:
        # Если пользователя нет, создаём новую запись
        cursor.execute("INSERT INTO users (user_id, preferences) VALUES (?, ?)", (user_id, preference))

    conn.commit()
    conn.close()


# Функция для получения предпочтений пользователя
def get_preferences(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT preferences FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    conn.close()
    return result[0] if result else None
