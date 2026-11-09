from flask import Flask, render_template, request, redirect, url_for, session, flash, g
import sqlite3

app = Flask(__name__)
# Secret key digunakan untuk mengamankan session flash message
app.secret_key = 'rahasia_hijau_perpustakaan'
DATABASE = 'database.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# --- ROUTE UTAMA & LOGIN ---
@app.route('/')
def index():
    if 'user_id' in session:
        if session['role'] == 'pustakawan':
            return redirect(url_for('pustakawan'))
        return redirect(url_for('peminjam'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('index'))
        else:
            flash('Username atau password salah!')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# --- ROUTE PUSTAKAWAN ---
@app.route('/pustakawan')
def pustakawan():
    if 'user_id' not in session or session['role'] != 'pustakawan':
        return redirect(url_for('login'))

    db = get_db()
    books = db.execute('SELECT * FROM books').fetchall()
    borrowings = db.execute('''
        SELECT b.id, u.username, bk.title, b.status 
        FROM borrowings b
        JOIN users u ON b.user_id = u.id
        JOIN books bk ON b.book_id = bk.id
    ''').fetchall()

    return render_template('pustakawan.html', books=books, borrowings=borrowings)


@app.route('/add_book', methods=['POST'])
def add_book():
    if 'user_id' in session and session['role'] == 'pustakawan':
        title = request.form['title']
        author = request.form['author']
        stock = int(request.form['stock'])

        db = get_db()
        db.execute('INSERT INTO books (title, author, stock) VALUES (?, ?, ?)', (title, author, stock))
        db.commit()
        flash('Buku berhasil ditambahkan!')
    return redirect(url_for('pustakawan'))


# --- ROUTE PEMINJAM ---
@app.route('/peminjam')
def peminjam():
    if 'user_id' not in session or session['role'] != 'peminjam':
        return redirect(url_for('login'))

    db = get_db()
    books = db.execute('SELECT * FROM books WHERE stock > 0').fetchall()
    my_borrowings = db.execute('''
        SELECT b.id, bk.title, b.status 
        FROM borrowings b
        JOIN books bk ON b.book_id = bk.id
        WHERE b.user_id = ?
    ''', (session['user_id'],)).fetchall()

    return render_template('peminjam.html', books=books, my_borrowings=my_borrowings)


@app.route('/borrow/<int:book_id>')
def borrow(book_id):
    if 'user_id' in session and session['role'] == 'peminjam':
        db = get_db()
        book = db.execute('SELECT stock FROM books WHERE id = ?', (book_id,)).fetchone()

        if book and book['stock'] > 0:
            db.execute('INSERT INTO borrowings (user_id, book_id, status) VALUES (?, ?, ?)',
                       (session['user_id'], book_id, 'dipinjam'))
            db.execute('UPDATE books SET stock = stock - 1 WHERE id = ?', (book_id,))
            db.commit()
            flash('Buku berhasil dipinjam!')
    return redirect(url_for('peminjam'))


@app.route('/return_book/<int:borrow_id>')
def return_book(borrow_id):
    if 'user_id' in session and session['role'] == 'peminjam':
        db = get_db()
        borrowing = db.execute('SELECT * FROM borrowings WHERE id = ? AND user_id = ? AND status = ?',
                               (borrow_id, session['user_id'], 'dipinjam')).fetchone()

        if borrowing:
            db.execute('UPDATE borrowings SET status = ? WHERE id = ?', ('dikembalikan', borrow_id))
            db.execute('UPDATE books SET stock = stock + 1 WHERE id = ?', (borrowing['book_id'],))
            db.commit()
            flash('Buku berhasil dikembalikan!')
    return redirect(url_for('peminjam'))


if __name__ == '__main__':
    app.run(debug=True)