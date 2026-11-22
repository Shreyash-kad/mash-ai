import sqlite3
from datetime import datetime
import os


# ============================================================
# DATABASE LOCATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DB_NAME = os.path.join(
    BASE_DIR,
    "chatbot.db"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    connection = sqlite3.connect(
        DB_NAME
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


# ============================================================
# CREATE DATABASE
# ============================================================

def create_database():

    connection = get_connection()

    cursor = connection.cursor()

    # ========================================================
    # CHATS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL
            DEFAULT 'New Chat',

            pinned INTEGER NOT NULL
            DEFAULT 0,

            created_at TEXT NOT NULL,

            updated_at TEXT NOT NULL
        )
    """)

    # ========================================================
    # MESSAGES
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            chat_id INTEGER NOT NULL,

            role TEXT NOT NULL,

            message TEXT NOT NULL,

            created_at TEXT NOT NULL,

            FOREIGN KEY (chat_id)
            REFERENCES chats(id)
            ON DELETE CASCADE
        )
    """)

    # ========================================================
    # DOCUMENTS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            chat_id INTEGER,

            filename TEXT NOT NULL,

            file_path TEXT NOT NULL,

            file_type TEXT,

            chunk_count INTEGER DEFAULT 0,

            created_at TEXT NOT NULL,

            FOREIGN KEY (chat_id)
            REFERENCES chats(id)
            ON DELETE CASCADE
        )
    """)

    # ========================================================
    # LONG-TERM MEMORY
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_memory (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            memory_key TEXT NOT NULL UNIQUE,

            memory_value TEXT NOT NULL,

            created_at TEXT NOT NULL,

            updated_at TEXT NOT NULL
        )
    """)

    connection.commit()

    # ========================================================
    # DATABASE MIGRATION
    #
    # This fixes OLD chatbot.db files.
    # ========================================================

    migrate_documents_table(
        connection
    )

    connection.close()


# ============================================================
# DOCUMENT TABLE MIGRATION
# ============================================================

def migrate_documents_table(connection):

    cursor = connection.cursor()

    cursor.execute("""
        PRAGMA table_info(documents)
    """)

    columns = [
        row["name"]
        for row in cursor.fetchall()
    ]

    # --------------------------------------------------------
    # ADD file_type IF MISSING
    # --------------------------------------------------------

    if "file_type" not in columns:

        cursor.execute("""
            ALTER TABLE documents
            ADD COLUMN file_type TEXT
        """)

        print(
            "Database migration: added file_type column."
        )

    # --------------------------------------------------------
    # ADD chunk_count IF MISSING
    # --------------------------------------------------------

    if "chunk_count" not in columns:

        cursor.execute("""
            ALTER TABLE documents
            ADD COLUMN chunk_count INTEGER DEFAULT 0
        """)

        print(
            "Database migration: added chunk_count column."
        )

    connection.commit()


# ============================================================
# CHAT FUNCTIONS
# ============================================================

def create_chat(
    title="New Chat"
):

    connection = get_connection()

    cursor = connection.cursor()

    now = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO chats
        (
            title,
            pinned,
            created_at,
            updated_at
        )

        VALUES (?, 0, ?, ?)
    """, (
        title,
        now,
        now
    ))

    chat_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return chat_id


def get_chats():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            title,
            pinned,
            created_at,
            updated_at

        FROM chats

        ORDER BY
            pinned DESC,
            updated_at DESC
    """)

    chats = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return chats


def get_chat(
    chat_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            title,
            pinned,
            created_at,
            updated_at

        FROM chats

        WHERE id = ?
    """, (
        chat_id,
    ))

    row = cursor.fetchone()

    connection.close()

    if row:
        return dict(row)

    return None


def update_chat_title(
    chat_id,
    title
):

    connection = get_connection()

    cursor = connection.cursor()

    now = datetime.now().isoformat()

    cursor.execute("""
        UPDATE chats

        SET
            title = ?,
            updated_at = ?

        WHERE id = ?
    """, (
        title,
        now,
        chat_id
    ))

    connection.commit()

    connection.close()


def update_chat_time(
    chat_id
):

    connection = get_connection()

    cursor = connection.cursor()

    now = datetime.now().isoformat()

    cursor.execute("""
        UPDATE chats

        SET updated_at = ?

        WHERE id = ?
    """, (
        now,
        chat_id
    ))

    connection.commit()

    connection.close()


def toggle_pin(
    chat_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE chats

        SET pinned =
            CASE
                WHEN pinned = 1
                THEN 0
                ELSE 1
            END

        WHERE id = ?
    """, (
        chat_id,
    ))

    connection.commit()

    connection.close()


def delete_chat(
    chat_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM chats

        WHERE id = ?
    """, (
        chat_id,
    ))

    connection.commit()

    connection.close()


# ============================================================
# MESSAGE FUNCTIONS
# ============================================================

def save_message(
    chat_id,
    role,
    message
):

    connection = get_connection()

    cursor = connection.cursor()

    now = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO messages
        (
            chat_id,
            role,
            message,
            created_at
        )

        VALUES (?, ?, ?, ?)
    """, (
        chat_id,
        role,
        message,
        now
    ))

    cursor.execute("""
        UPDATE chats

        SET updated_at = ?

        WHERE id = ?
    """, (
        now,
        chat_id
    ))

    connection.commit()

    connection.close()


def get_messages(
    chat_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            chat_id,
            role,
            message,
            created_at

        FROM messages

        WHERE chat_id = ?

        ORDER BY id ASC
    """, (
        chat_id,
    ))

    messages = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return messages


# ============================================================
# DOCUMENT FUNCTIONS
# ============================================================

def save_document(
    chat_id,
    filename,
    file_path,
    file_type=None,
    chunk_count=0
):

    connection = get_connection()

    cursor = connection.cursor()

    now = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO documents
        (
            chat_id,
            filename,
            file_path,
            file_type,
            chunk_count,
            created_at
        )

        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        chat_id,
        filename,
        file_path,
        file_type,
        chunk_count,
        now
    ))

    document_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return document_id


def get_documents(
    chat_id=None
):

    connection = get_connection()

    cursor = connection.cursor()

    if chat_id is None:

        cursor.execute("""
            SELECT
                id,
                chat_id,
                filename,
                file_path,
                file_type,
                chunk_count,
                created_at

            FROM documents

            ORDER BY id DESC
        """)

    else:

        cursor.execute("""
            SELECT
                id,
                chat_id,
                filename,
                file_path,
                file_type,
                chunk_count,
                created_at

            FROM documents

            WHERE chat_id = ?

            ORDER BY id DESC
        """, (
            chat_id,
        ))

    documents = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return documents


def get_document(
    document_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            chat_id,
            filename,
            file_path,
            file_type,
            chunk_count,
            created_at

        FROM documents

        WHERE id = ?
    """, (
        document_id,
    ))

    row = cursor.fetchone()

    connection.close()

    if row:
        return dict(row)

    return None


def delete_document(
    document_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM documents

        WHERE id = ?
    """, (
        document_id,
    ))

    connection.commit()

    connection.close()


# ============================================================
# LONG-TERM MEMORY FUNCTIONS
# ============================================================

def save_memory(
    key,
    value
):

    connection = get_connection()

    cursor = connection.cursor()

    now = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO user_memory
        (
            memory_key,
            memory_value,
            created_at,
            updated_at
        )

        VALUES (?, ?, ?, ?)

        ON CONFLICT(memory_key)

        DO UPDATE SET

            memory_value =
                excluded.memory_value,

            updated_at =
                excluded.updated_at
    """, (
        key,
        value,
        now,
        now
    ))

    connection.commit()

    connection.close()


def get_memories():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            memory_key AS key,
            memory_value AS value,
            created_at,
            updated_at

        FROM user_memory

        ORDER BY updated_at DESC
    """)

    memories = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return memories


def delete_memory(
    key
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM user_memory

        WHERE memory_key = ?
    """, (
        key,
    ))

    connection.commit()

    connection.close()