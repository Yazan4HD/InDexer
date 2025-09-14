# database.py

import sqlite3
import os

# Define the database file name
DB_FILE = "file_index.db"

def init_db():
    """
    Initializes the database and creates tables if they don't exist.
    """
    # The connect() function will create the file if it doesn't exist
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Table to store the root folders you've added to be indexed
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS indexed_folders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT NOT NULL UNIQUE
    );
    """)

    # Table to store details of every single file found
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        folder_id INTEGER,
        name TEXT NOT NULL,
        directory TEXT NOT NULL,
        size_bytes INTEGER,
        creation_date TEXT,
        modification_date TEXT,
        FOREIGN KEY (folder_id) REFERENCES indexed_folders (id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()

# Let's initialize the database when this script is first imported
if not os.path.exists(DB_FILE):
    print("Database not found, creating a new one...")
    init_db()
