
import sqlite3
from datetime import datetime
from contextlib import contextmanager
import json

DATABASE_FILE = 'wallet_system.db'

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_database():
    """Initialize the database with required tables"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Table to store student-wallet mappings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                student_name TEXT NOT NULL,
                wallet_id TEXT UNIQUE NOT NULL,
                phone TEXT,
                email TEXT,
                balance REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Table to store transaction history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT UNIQUE,
                type TEXT NOT NULL,
                student_id TEXT,
                from_student TEXT,
                to_student TEXT,
                amount REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                description TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ''')

        # Create indexes for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_student_id ON wallets(student_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_wallet_id ON wallets(wallet_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transaction_type ON transactions(type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transaction_timestamp ON transactions(timestamp)')

        conn.commit()
        print("Database initialized successfully")

def add_wallet(student_id, student_name, wallet_id, phone=None, email=None):
    """Add a new wallet to the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO wallets (student_id, student_name, wallet_id, phone, email)
            VALUES (?, ?, ?, ?, ?)
        ''', (student_id, student_name, wallet_id, phone, email))
        return cursor.lastrowid

def get_wallet_by_student_id(student_id):
    """Get wallet information by student ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM wallets WHERE student_id = ?', (student_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def get_wallet_by_wallet_id(wallet_id):
    """Get wallet information by wallet ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM wallets WHERE wallet_id = ?', (wallet_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def update_wallet_balance(student_id, balance):
    """Update wallet balance"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE wallets
            SET balance = ?, updated_at = CURRENT_TIMESTAMP
            WHERE student_id = ?
        ''', (balance, student_id))
        return cursor.rowcount > 0

def get_all_wallets():
    """Get all wallets from the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM wallets ORDER BY created_at DESC')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def add_transaction(transaction_type, amount, status='pending', student_id=None,
                   from_student=None, to_student=None, description=None,
                   transaction_id=None, metadata=None):
    """Add a new transaction to the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Convert metadata dict to JSON string if provided
        metadata_json = json.dumps(metadata) if metadata else None

        cursor.execute('''
            INSERT INTO transactions
            (transaction_id, type, student_id, from_student, to_student, amount, status, description, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (transaction_id, transaction_type, student_id, from_student, to_student,
              amount, status, description, metadata_json))
        return cursor.lastrowid

def update_transaction_status(transaction_id, status):
    """Update transaction status"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE transactions
            SET status = ?
            WHERE transaction_id = ?
        ''', (status, transaction_id))
        return cursor.rowcount > 0

def get_all_transactions(limit=50):
    """Get all transactions from the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM transactions
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        transactions = []
        for row in rows:
            txn = dict(row)
            # Parse metadata JSON if exists
            if txn.get('metadata'):
                try:
                    txn['metadata'] = json.loads(txn['metadata'])
                except:
                    pass
            transactions.append(txn)
        return transactions

def get_transactions_by_student(student_id, limit=50):
    """Get all transactions for a specific student"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM transactions
            WHERE student_id = ? OR from_student = ? OR to_student = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (student_id, student_id, student_id, limit))
        rows = cursor.fetchall()
        transactions = []
        for row in rows:
            txn = dict(row)
            if txn.get('metadata'):
                try:
                    txn['metadata'] = json.loads(txn['metadata'])
                except:
                    pass
            transactions.append(txn)
        return transactions

# Initialize database when module is imported
init_database()
