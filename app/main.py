from fastapi import FastAPI
from datetime import datetime

from app.model import (
    AuthorizationRequest,
    AuthorizationResponse,
    PreVerificationRequest,
    PreVerificationResponse
)

from app.authorize import AuthorizationEngine

app = FastAPI(title="OveRide Fraud Protection API")

# Initialize the authorization engine
auth_engine = AuthorizationEngine()

# Root Endpoint
@app.get("/")
def root():
    return {"message": "OveRide API running"}

# Authorize Transaction

@app.post("/authorize", response_model=AuthorizationResponse)
def authorize(request: AuthorizationRequest):
    return auth_engine.authorize_transaction(request)

# Pre-Verify Transaction
@app.post("/preverify", response_model=PreVerificationResponse)
def preverify(request: PreVerificationRequest):
    return auth_engine.pre_verify_transaction(request)

# Merchant Analytics
@app.get("/analytics/{merchant_id}")
def analytics(merchant_id: str):
    start = datetime.now()
    end = datetime.now()

    result = auth_engine.get_merchant_analytics(
        merchant_id,
        start,
        end
    )

    return result

# Transaction History
@app.get("/transactions")
def transactions():
    return auth_engine.get_transaction_history()