import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Tabel Users (Pustakawan & Peminjam)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL -- 'pustakawan' atau 'peminjam'
        )
    ''')

    # Tabel Books
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')

    # Tabel Borrowings (Peminjaman)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS borrowings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            book_id INTEGER,
            status TEXT NOT NULL, -- 'dipinjam' atau 'dikembalikan'
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (book_id) REFERENCES books (id)
        )
    ''')

    # Insert akun Pustakawan dan Peminjam default jika belum ada
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'pustakawan')")
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('nasrul', 'user123', 'peminjam')")

    # Insert beberapa buku default
    cursor.execute("SELECT * FROM books")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO books (title, author, stock) VALUES ('Pemrograman Python', 'Budi', 5)")
        cursor.execute("INSERT INTO books (title, author, stock) VALUES ('Dasar Web Design', 'Andi', 3)")

    conn.commit()
    conn.close()
    print("Database berhasil diinisialisasi!")

if __name__ == '__main__':
    init_db()