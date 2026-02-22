# OveRide <br/>
OveRide is a authorization layer that lets consumers pre-verify high-risk purchases. It converts fraud-prone transactions to instant approvals while giving merchants visibility into prevented revenue loss.

## Features<br/>
- Risk scoring engine 
- Pre-verification flow 
- Authorization decisions (approve, decline, pre-verified approve)
- Merchant analytics (revenue saved, fraud prevented, approval rates)

## File structure<br/>
OveRide/
- app/
  - main.py
  - model.py
  - risk_engine.py
  - authorization_engine.py
- data/
- requirements.txt

## Getting started<br/> 
1) Install dependencies:
	pip install -r requirements.txt

2) Run the API:
	python app/main.py

3) Open docs:
	http://localhost:8000/docs

### API endpoints
POST /api/v1/pre-verify
Pre-verify a high-risk transaction before purchase.

POST /api/v1/authorize
Authorize a transaction with real-time risk assessment.

GET /api/v1/analytics/{merchant_id}?days=7
Merchant analytics showing revenue saved and fraud prevented.

GET /api/v1/transactions?limit=50
Recent transactions for monitoring.

Example flow
------------
1) Customer pre-verifies a high-risk purchase.
2) Customer submits authorization with token.
3) High-risk transaction is approved and revenue_saved is recorded.

Development notes
-----------------
- This is a simulation. Tokens, risk factors, and analytics are in-memory.
- For production: add persistence, real verification (SMS/email/biometric), and auth.

Next steps
----------
- Add database persistence (Postgres/Redis)
- Integrate real verification providers
- Add web dashboard for merchants


