import sqlite3

def create_connection():
    conn = sqlite3.connect('project.db')
    return conn

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            categories TEXT,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Jalankan fungsi create_table saat file di-import
create_table()