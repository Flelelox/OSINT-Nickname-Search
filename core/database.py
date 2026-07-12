"""
SQLite база данных проекта.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

DB_DIR = Path("data")
DB_DIR.mkdir(exist_ok=True)

DB_PATH = DB_DIR / "osint.db"


class Database:

    def __init__(self):

        self.connection = sqlite3.connect(DB_PATH)

        self.connection.row_factory = sqlite3.Row

        self.create_tables()

    # =========================================================

    def create_tables(self):

        cursor = self.connection.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS history(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT NOT NULL,

            searched_at TEXT DEFAULT CURRENT_TIMESTAMP

        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS results(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT,

            service TEXT,

            profile_url TEXT,

            similarity REAL,

            exists_profile INTEGER,

            display_name TEXT,

            biography TEXT,

            avatar_url TEXT,

            website TEXT,

            followers INTEGER,

            created_at TEXT

        )
        """)

        self.connection.commit()

    # =========================================================

    def add_history(self, username: str):

        cursor = self.connection.cursor()

        cursor.execute(

            """
            INSERT INTO history(username)
            VALUES(?)
            """,

            (username,)

        )

        self.connection.commit()

    # =========================================================

    def save_result(self, result):

        cursor = self.connection.cursor()

        cursor.execute("""

        INSERT INTO results(

            username,

            service,

            profile_url,

            similarity,

            exists_profile,

            display_name,

            biography,

            avatar_url,

            website,

            followers,

            created_at

        )

        VALUES(?,?,?,?,?,?,?,?,?,?,?)

        """,

        (

            result.username,

            result.service,

            result.profile_url,

            result.similarity,

            int(result.exists),

            result.display_name,

            result.biography,

            result.avatar_url,

            result.website,

            result.followers,

            result.created_at

        )

        )

        self.connection.commit()

    # =========================================================

    def history(self):

        cursor = self.connection.cursor()

        cursor.execute("""

        SELECT *

        FROM history

        ORDER BY id DESC

        """)

        return cursor.fetchall()

    # =========================================================

    def clear(self):

        cursor = self.connection.cursor()

        cursor.execute("DELETE FROM history")

        cursor.execute("DELETE FROM results")

        self.connection.commit()

    # =========================================================

    def close(self):

        self.connection.close()