from app.repository.transaction import TransactionRepository
from app.core.population import generate_transaction


def seed_transaction_history(customers: dict, transactions_per_customer=100):
    repo = TransactionRepository()

    for traits in customers.values():
        for _ in range(transactions_per_customer):

            tx_data = generate_transaction(traits)

            # Fake approval + risk for historical realism
            repo.save_transaction_from_seed(
                transaction_id=tx_data["transaction_id"],
                customer_id=tx_data["customer_id"],
                merchant_id=tx_data["merchant_id"],
                amount=tx_data["amount"],
                timestamp=tx_data["timestamp"]
            )