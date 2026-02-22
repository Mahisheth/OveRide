from fastapi import FastAPI
from app.authorize import AuthorizationEngine
from app.model import AuthorizationRequest, PreVerificationRequest

app = FastAPI(title="Mock Bank API")

engine = AuthorizationEngine()


@app.post("/pre-verify")
def pre_verify(request: PreVerificationRequest):
    return engine.pre_verify_transaction(request)


@app.post("/authorize")
def authorize(request: AuthorizationRequest):
    return engine.authorize_transaction(request)


@app.get("/health")
def health():
    return {"status": "Bank API running"}