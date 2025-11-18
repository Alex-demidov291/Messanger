from flask import Flask, request, jsonify
import sqlite3
import uuid
import datetime
import os

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def init_db():
    conn = sqlite3.connect('messenger.db', check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            login TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            avatar TEXT DEFAULT 'default_avatar.jpg',
            user_token TEXT UNIQUE,
            user_id INTEGER UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_login TEXT NOT NULL,
            receiver_login TEXT NOT NULL,
            message_text TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_login) REFERENCES users (login),
            FOREIGN KEY (receiver_login) REFERENCES users (login)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_owner TEXT NOT NULL,
            contact_login TEXT NOT NULL,
            FOREIGN KEY (contact_owner) REFERENCES users(login),
            FOREIGN KEY (contact_login) REFERENCES users(login),
            UNIQUE(contact_owner, contact_login)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contact_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_login TEXT NOT NULL,
            contact_login TEXT NOT NULL,
            display_name TEXT,
            FOREIGN KEY (user_login) REFERENCES users(login),
            FOREIGN KEY (contact_login) REFERENCES users(login),
            UNIQUE(user_login, contact_login)
        )
    ''')

    conn.commit()
    conn.close()


init_db()


def get_db_connection():
    conn = sqlite3.connect('messenger.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def get_user_by_token(user_token, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_token = ? AND user_id = ?', (user_token, user_id))
    user = cursor.fetchone()
    conn.close()
    return user


@app.route('/')
def hello():
    return 'Messenger Server is running!'


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    login = data.get('login')
    password = data.get('password')
    username = data.get('username')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE login = ? OR username = ?', (login, username))
    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        return jsonify({'success': False, 'error': 'Логин или имя уже заняты'})

    user_token = str(uuid.uuid4())
    user_id = int(datetime.datetime.now().timestamp() * 1000000) % 1000000000

    cursor.execute('''
        INSERT INTO users (login, password, username, user_token, user_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (login, password, username, user_token, user_id))

    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'user_token': user_token,
        'user_id': user_id
    })


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    login = data.get('login')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE login = ?', (login,))
    user = cursor.fetchone()
    conn.close()

    if not user or user['password'] != password:
        return jsonify({'success': False, 'error': 'Неверный логин или пароль'})

    return jsonify({
        'success': True,
        'user_token': user['user_token'],
        'user_id': user['user_id'],
        'username': user['username']
    })


@app.route('/api/info', methods=['POST'])
def get_info():
    data = request.get_json()
    user_token = data.get('user_token')
    user_id = data.get('user_id')

    user = get_user_by_token(user_token, user_id)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT login, username, avatar FROM users')
    users = []
    rows = cursor.fetchall()
    for row in rows:
        user_dict = dict(row)
        users.append(user_dict)

    conn.close()

    return jsonify({
        'success': True,
        'user_id': user['user_id'],
        'username': user['username'],
        'avatar': user['avatar'],
        'users': users
    })


@app.route('/api/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    user_token = data.get('user_token')
    user_id = data.get('user_id')
    receiver_login = data.get('receiver_login')
    text = data.get('text')

    user = get_user_by_token(user_token, user_id)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO messages (sender_login, receiver_login, message_text)
        VALUES (?, ?, ?)
    ''', (user['login'], receiver_login, text))

    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route('/api/get_messages', methods=['POST'])
def get_messages():
    data = request.get_json()
    user_token = data.get('user_token')
    user_id = data.get('user_id')
    other_user_login = data.get('other_user_login')

    user = get_user_by_token(user_token, user_id)
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT m.*, u.username as sender_name
        FROM messages m
        JOIN users u ON m.sender_login = u.login
        WHERE (m.sender_login = ? AND m.receiver_login = ?) 
           OR (m.sender_login = ? AND m.receiver_login = ?)
        ORDER BY m.timestamp ASC
    ''', (user['login'], other_user_login, other_user_login, user['login']))

    messages = []
    rows = cursor.fetchall()
    for row in rows:
        message_dict = dict(row)
        messages.append(message_dict)
    conn.close()

    return jsonify({'success': True, 'messages': messages})


@app.route('/api/update_profile', methods=['POST'])
def update_profile():
    data = request.get_json()
    user_token = data.get('user_token')
    user_id = data.get('user_id')
    username = data.get('username')
    avatar = data.get('avatar')
    password = data.get('password')

    user = get_user_by_token(user_token, user_id)

    conn = get_db_connection()
    cursor = conn.cursor()

    if username:
        cursor.execute('UPDATE users SET username = ? WHERE user_token = ? AND user_id = ?',
                       (username, user_token, user_id))

    if avatar:
        cursor.execute('UPDATE users SET avatar = ? WHERE user_token = ? AND user_id = ?',
                       (avatar, user_token, user_id))

    if password:
        cursor.execute('UPDATE users SET password = ? WHERE user_token = ? AND user_id = ?',
                       (password, user_token, user_id))

    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route('/api/add_contact', methods=['POST'])
def add_contact():
    data = request.get_json()
    user_token = data.get('user_token')
    user_id = data.get('user_id')
    contact_login = data.get('contact_login')

    user = get_user_by_token(user_token, user_id)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('INSERT INTO contacts (contact_owner, contact_login) VALUES (?, ?)', (user['login'], contact_login))
    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route('/api/get_contacts', methods=['POST'])
def get_contacts():
    data = request.get_json()
    user_token = data.get('user_token')
    user_id = data.get('user_id')

    user = get_user_by_token(user_token, user_id)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT u.login, u.username, u.avatar
        FROM contacts c 
        JOIN users u ON c.contact_login = u.login 
        WHERE c.contact_owner = ?
        ORDER BY u.username
    ''', (user['login'],))

    contacts = []
    for row in cursor.fetchall():
        contacts.append({
            'login': row['login'],
            'username': row['username'],
            'avatar': row['avatar']
        })

    conn.close()
    return jsonify({'success': True, 'contacts': contacts})


@app.route('/api/save_contact_settings', methods=['POST'])
def save_contact_settings():
    data = request.get_json()
    user_token = data.get('user_token')
    user_id = data.get('user_id')
    contact_login = data.get('contact_login')
    display_name = data.get('display_name')

    user = get_user_by_token(user_token, user_id)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO contact_settings 
        (user_login, contact_login, display_name)
        VALUES (?, ?, ?)
    ''', (user['login'], contact_login, display_name))

    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route('/api/get_contact_settings', methods=['POST'])
def get_contact_settings():
    data = request.get_json()
    user_token = data.get('user_token')
    user_id = data.get('user_id')

    user = get_user_by_token(user_token, user_id)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT contact_login, display_name 
        FROM contact_settings 
        WHERE user_login = ?
    ''', (user['login'],))

    settings = {}
    for row in cursor.fetchall():
        settings[row['contact_login']] = {
            'display_name': row['display_name']
        }

    conn.close()
    return jsonify({'success': True, 'settings': settings})


@app.route('/api/remove_contact', methods=['POST'])
def remove_contact():
    data = request.get_json()
    user_token = data.get('user_token')
    user_id = data.get('user_id')
    contact_login = data.get('contact_login')

    user = get_user_by_token(user_token, user_id)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM contacts WHERE contact_owner = ? AND contact_login = ?', (user['login'], contact_login))
    conn.commit()
    conn.close()

    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)