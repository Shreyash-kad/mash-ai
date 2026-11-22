import sqlite3

DB_NAME = "chatbot.db"


def get_connection():
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def save_message(chat_id, role, message):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO messages(chat_id, role, message, created_at)
        VALUES (?, ?, ?, datetime('now'))
    """, (
        chat_id,
        role,
        message
    ))

    connection.commit()
    connection.close()


def get_history(chat_id, limit=10):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT role, message
        FROM messages
        WHERE chat_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (
        chat_id,
        limit
    ))

    rows = cursor.fetchall()

    connection.close()

    rows.reverse()

    history = []

    for row in rows:

        history.append({
            "role": row["role"],
            "message": row["message"]
        })

    return history


def get_messages(chat_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, role, message, created_at
        FROM messages
        WHERE chat_id = ?
        ORDER BY id ASC
    """, (chat_id,))

    messages = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return messages


def clear_chat_messages(chat_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM messages
        WHERE chat_id = ?
    """, (chat_id,))

    connection.commit()
    connection.close()