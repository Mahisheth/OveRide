import sqlite3
from datetime import datetime

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

    def save_transaction(self, transaction, auth_response):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction.transaction_id,
                transaction.customer_id,
                transaction.merchant_id,
                transaction.amount,
                auth_response.risk_assessment.risk_score,
                auth_response.risk_assessment.risk_level,
                int(auth_response.approved),
                auth_response.message,
                auth_response.revenue_saved,
                transaction.timestamp.isoformat()
            ))
            conn.commit()

    def get_all_transactions(self):
        with sqlite3.connect(DB_NAME) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transactions")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]