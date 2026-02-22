import sqlite3
from datetime import datetime

DB_NAME = "transactions.db"


class TransactionRepository:
    import sqlite3

DB_NAME = "transactions.db"

class TransactionRepository:

    def __init__(self):
        self._initialize_db()

    def _initialize_db(self):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id TEXT PRIMARY KEY,
                    customer_id TEXT,
                    merchant_id TEXT,
                    amount REAL,
                    risk_score REAL,
                    risk_level TEXT,
                    approved INTEGER,
                    message TEXT,
                    revenue_saved REAL,
                    timestamp TEXT
                )
            """)
            conn.commit()
            
    def save_transaction_from_seed(
        self,
        transaction_id,
        customer_id,
        merchant_id,
        amount,
        timestamp
    ):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction_id,
                customer_id,
                merchant_id,
                amount,
                0.0,                 # risk_score
                "LOW",               # risk_level
                1,                   # approved
                "Historical seed",   # message
                amount,              # revenue_saved
                timestamp.isoformat()
            ))
            conn.commit()