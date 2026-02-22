import random
import uuid
from datetime import datetime, timedelta
import numpy as np


INCOME_DISTRIBUTION = {
    "low": (50, 0.6),     # mean, sigma
    "mid": (400, 0.7),
    "high": (2500, 0.8)
}

MERCHANTS = [f"merchant_{i:03d}" for i in range(1, 201)]


class CustomerTraits:
    def __init__(self, customer_id: str):
        random.seed(hash(customer_id))

        self.customer_id = customer_id
        self.income = random.choice(["low", "mid", "high"])
        self.mean_spend, self.sigma = INCOME_DISTRIBUTION[self.income]
        self.active_start = random.randint(6, 10)
        self.active_end = random.randint(18, 23)
        self.merchant_pool = random.sample(
            MERCHANTS, 
            random.randint(5, 25)
        )
        self.volatility = random.uniform(0.8, 1.5)
        self.base_risk = random.uniform(0.01, 0.2)


def generate_population(n: int):
    customers = {}
    for i in range(n):
        cid = f"cust_{i:05d}"
        customers[cid] = CustomerTraits(cid)
    return customers


def generate_transaction(traits: CustomerTraits):
    amount = np.random.lognormal(
        mean=np.log(traits.mean_spend),
        sigma=traits.sigma * traits.volatility
    )

    merchant = random.choice(traits.merchant_pool)

    hour = random.randint(traits.active_start, traits.active_end)

    timestamp = datetime.now() - timedelta(
        days=random.randint(1, 180),
        hours=random.randint(0, 23)
    )

    return {
        "transaction_id": str(uuid.uuid4()),
        "customer_id": traits.customer_id,
        "merchant_id": merchant,
        "amount": round(float(amount), 2),
        "timestamp": timestamp,
    }