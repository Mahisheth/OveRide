import sqlite3
from datetime import datetime

DB_PATH = "transactions.db"


class TransactionRepository:

    def __init__(self):
        self._initialize_db()

    def _initialize_db(self):
        with sqlite3.connect(DB_PATH) as conn:
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
    def get_unique_customers(self):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT customer_id FROM transactions")
            return [row[0] for row in cursor.fetchall()]

    def get_unique_merchants(self):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT merchant_id FROM transactions")
            return [row[0] for row in cursor.fetchall()]
    
    def get_all_transactions(self):
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transactions")
            return [dict(row) for row in cursor.fetchall()]

    def save_transaction_from_seed(
        self,
        transaction_id,
        customer_id,
        merchant_id,
        amount,
        timestamp
    ):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction_id,
                customer_id,
                merchant_id,
                amount,
                0.0,
                "LOW",
                1,
                "Historical seed",
                amount,
                timestamp.isoformat()
            ))
            conn.commit()

    def save_transaction(self, transaction, response):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction.transaction_id,
                transaction.customer_id,
                transaction.merchant_id,
                transaction.amount,
                response.risk_assessment.risk_score,
                response.risk_assessment.risk_level,
                int(response.approved),
                response.message,
                response.revenue_saved,
                transaction.timestamp.isoformat()
            ))
            conn.commit()