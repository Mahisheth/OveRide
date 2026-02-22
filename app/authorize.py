import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

from app.model import (
    AuthorizationRequest,
    AuthorizationResponse,
    TransactionStatus,
    PreVerificationRequest,
    PreVerificationResponse,
    Transaction
)

from app.risk_detection import RiskEngine
from app.repository.transaction import TransactionRepository
from app.core.population import generate_population
from app.core.history import seed_transaction_history


class AuthorizationEngine:

    def __init__(self):
        self.risk_engine = RiskEngine()
        self.repository = TransactionRepository()

        self.pre_verified_tokens: Dict[str, PreVerificationResponse] = {}
        self.transaction_history = []

        # Seed population only if DB empty
        if not self.repository.get_all_transactions():
            customers = generate_population(5000)
            seed_transaction_history(customers, transactions_per_customer=100)

    # ------------------------
    # PRE-VERIFICATION
    # ------------------------
    def pre_verify_transaction(
        self,
        request: PreVerificationRequest
    ) -> PreVerificationResponse:

        verification_token = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(minutes=15)

        key = f"{request.customer_id}:{request.amount}"

        response = PreVerificationResponse(
            verification_token=verification_token,
            expires_at=expires_at,
            verified=True,
            message="Pre-verification successful."
        )

        self.pre_verified_tokens[key] = response
        return response

    # ------------------------
    # AUTHORIZE TRANSACTION
    # ------------------------
    def authorize_transaction(
        self,
        request: AuthorizationRequest
    ) -> AuthorizationResponse:

        start_time = time.time()
        transaction = request.transaction

        risk_assessment = self.risk_engine.calculate_risk_score(transaction)

        is_pre_verified = self._check_pre_verification(
            transaction.customer_id,
            transaction.amount,
            request.customer_verification_token
        )

        status, approved, message, revenue_saved = self._make_decision(
            risk_assessment,
            is_pre_verified,
            transaction.amount
        )

        processing_time = (time.time() - start_time) * 1000

        response = AuthorizationResponse(
            transaction_id=transaction.transaction_id,
            status=status,
            risk_assessment=risk_assessment,
            approved=approved,
            message=message,
            processing_time_ms=processing_time,
            revenue_saved=revenue_saved
        )

        # Save to DB
        self.repository.save_transaction(transaction, response)

        self.transaction_history.append({
            'transaction': transaction,
            'response': response,
            'timestamp': datetime.utcnow(),
            'pre_verified': is_pre_verified
        })

        return response

    # ------------------------
    # HELPERS
    # ------------------------
    def _check_pre_verification(
        self,
        customer_id: str,
        amount: float,
        verification_token: Optional[str]
    ) -> bool:

        if not verification_token:
            return False

        key = f"{customer_id}:{amount}"
        stored_verification = self.pre_verified_tokens.get(key)

        if not stored_verification:
            return False

        if stored_verification.verification_token != verification_token:
            return False

        if datetime.now() > stored_verification.expires_at:
            return False

        return True

    def _make_decision(
        self,
        risk_assessment,
        is_pre_verified: bool,
        amount: float
    ) -> Tuple[TransactionStatus, bool, str, Optional[float]]:

        risk_score = risk_assessment.risk_score

        if risk_score < 50:
            return (
                TransactionStatus.APPROVED,
                True,
                "Transaction approved - Low risk",
                0.0
            )

        if is_pre_verified:
            return (
                TransactionStatus.PRE_VERIFIED,
                True,
                "Transaction approved via pre-verification.",
                amount
            )

        return (
            TransactionStatus.DECLINED,
            False,
            f"Transaction declined - High risk ({risk_score:.1f}/100).",
            0.0
        )