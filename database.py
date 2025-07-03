import sqlite3
import datetime
from typing import Dict, List, Optional

DB_NAME = "casino.db"

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            main_balance REAL DEFAULT 0,
            bonus_balance REAL DEFAULT 0,
            referrer_id INTEGER,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_deposited REAL DEFAULT 0,
            total_withdrawn REAL DEFAULT 0,
            games_played INTEGER DEFAULT 0,
            total_wagered REAL DEFAULT 0
        )
    ''')
    
    # Таблица транзакций
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            transaction_type TEXT,
            description TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # Таблица депозитов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deposits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            currency TEXT,
            invoice_id INTEGER,
            status TEXT DEFAULT 'pending',
            rub_amount REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # Таблица выводов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS withdrawals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            currency TEXT,
            check_id INTEGER,
            check_url TEXT,
            status TEXT DEFAULT 'pending',
            rub_amount REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_user(user_id: int) -> Optional[Dict]:
    """Получить пользователя по ID"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    
    conn.close()
    
    if user:
        return {
            'user_id': user[0],
            'username': user[1],
            'full_name': user[2],
            'main_balance': user[3],
            'bonus_balance': user[4],
            'referrer_id': user[5],
            'registration_date': user[6],
            'total_deposited': user[7],
            'total_withdrawn': user[8],
            'games_played': user[9],
            'total_wagered': user[10]
        }
    return None

def create_user(user_id: int, username: str, full_name: str, referrer_id: int = None):
    """Создать нового пользователя"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO users (user_id, username, full_name, referrer_id)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, full_name, referrer_id))
    
    conn.commit()
    conn.close()

def get_user_balance(user_id: int) -> Dict[str, float]:
    """Получить баланс пользователя"""
    user = get_user(user_id)
    if user:
        return {
            'main': user['main_balance'],
            'bonus': user['bonus_balance']
        }
    return {'main': 0.0, 'bonus': 0.0}

def update_balance(user_id: int, amount: float, balance_type: str = 'main'):
    """Обновить баланс пользователя"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if balance_type == 'main':
        cursor.execute('''
            UPDATE users SET main_balance = main_balance + ?
            WHERE user_id = ?
        ''', (amount, user_id))
    else:
        cursor.execute('''
            UPDATE users SET bonus_balance = bonus_balance + ?
            WHERE user_id = ?
        ''', (amount, user_id))
    
    conn.commit()
    conn.close()

def add_transaction(user_id: int, amount: float, transaction_type: str, description: str):
    """Добавить транзакцию"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO transactions (user_id, amount, transaction_type, description)
        VALUES (?, ?, ?, ?)
    ''', (user_id, amount, transaction_type, description))
    
    conn.commit()
    conn.close()

def get_user_transactions(user_id: int, limit: int = 10) -> List[Dict]:
    """Получить транзакции пользователя"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM transactions 
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (user_id, limit))
    
    transactions = cursor.fetchall()
    conn.close()
    
    return [
        {
            'id': t[0],
            'user_id': t[1],
            'amount': t[2],
            'type': t[3],
            'description': t[4],
            'timestamp': t[5]
        }
        for t in transactions
    ]

def create_deposit(user_id: int, amount: float, currency: str, invoice_id: int, rub_amount: float):
    """Создать запись о депозите"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO deposits (user_id, amount, currency, invoice_id, rub_amount)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, amount, currency, invoice_id, rub_amount))
    
    conn.commit()
    conn.close()

def update_deposit_status(invoice_id: int, status: str):
    """Обновить статус депозита"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE deposits SET status = ? WHERE invoice_id = ?
    ''', (status, invoice_id))
    
    conn.commit()
    conn.close()

def get_deposit_by_invoice(invoice_id: int) -> Optional[Dict]:
    """Получить депозит по ID счета"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM deposits WHERE invoice_id = ?', (invoice_id,))
    deposit = cursor.fetchone()
    
    conn.close()
    
    if deposit:
        return {
            'id': deposit[0],
            'user_id': deposit[1],
            'amount': deposit[2],
            'currency': deposit[3],
            'invoice_id': deposit[4],
            'status': deposit[5],
            'rub_amount': deposit[6],
            'timestamp': deposit[7]
        }
    return None

def create_withdrawal(user_id: int, amount: float, currency: str, check_id: int, 
                     check_url: str, rub_amount: float):
    """Создать запись о выводе"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO withdrawals (user_id, amount, currency, check_id, check_url, rub_amount)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, amount, currency, check_id, check_url, rub_amount))
    
    conn.commit()
    conn.close()

def update_withdrawal_status(check_id: int, status: str):
    """Обновить статус вывода"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE withdrawals SET status = ? WHERE check_id = ?
    ''', (status, check_id))
    
    conn.commit()
    conn.close()

def get_all_users() -> List[Dict]:
    """Получить всех пользователей (для админки)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users ORDER BY registration_date DESC')
    users = cursor.fetchall()
    
    conn.close()
    
    return [
        {
            'user_id': user[0],
            'username': user[1],
            'full_name': user[2],
            'main_balance': user[3],
            'bonus_balance': user[4],
            'referrer_id': user[5],
            'registration_date': user[6],
            'total_deposited': user[7],
            'total_withdrawn': user[8],
            'games_played': user[9],
            'total_wagered': user[10]
        }
        for user in users
    ]

def get_bot_stats() -> Dict:
    """Получить статистику бота"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Общее количество пользователей
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    # Общий баланс
    cursor.execute('SELECT SUM(main_balance + bonus_balance) FROM users')
    total_balance = cursor.fetchone()[0] or 0
    
    # Общее количество игр
    cursor.execute('SELECT SUM(games_played) FROM users')
    total_games = cursor.fetchone()[0] or 0
    
    # Общая сумма ставок
    cursor.execute('SELECT SUM(total_wagered) FROM users')
    total_wagered = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        'total_users': total_users,
        'total_balance': total_balance,
        'total_games': total_games,
        'total_wagered': total_wagered
    }

def update_user_stats(user_id: int, wagered_amount: float):
    """Обновить статистику пользователя"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users 
        SET games_played = games_played + 1,
            total_wagered = total_wagered + ?
        WHERE user_id = ?
    ''', (wagered_amount, user_id))
    
    conn.commit()
    conn.close()