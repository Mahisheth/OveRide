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


class AuthorizationEngine:
    
    def __init__(self):
        self.risk_engine = RiskEngine()
        self.pre_verified_tokens: Dict[str, PreVerificationResponse] = {}
        self.transaction_history = []
    
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
            message="Pre-verification successful. You can now complete your purchase."
        )
        self.pre_verified_tokens[key] = response
        return response
    
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
        
        self.transaction_history.append({
            'transaction': transaction,
            'response': response,
            'timestamp': datetime.utcnow(),
            'pre_verified': is_pre_verified
        })
        return response
    
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
        amount: float) -> Tuple[TransactionStatus, bool, str, Optional[float]]:
        risk_score = risk_assessment.risk_score
        
        # Case 1: Low/Medium risk - Standard approval
        if risk_score < 50:
            return (
                TransactionStatus.APPROVED,
                True,
                "Transaction approved - Low risk",
                0.0
            )
        
        # Case 2: High/Critical risk with pre-verification
        if is_pre_verified:
            return (
                TransactionStatus.PRE_VERIFIED,
                True,
                f"Transaction approved via pre-verification. "
                f"High-risk transaction converted to instant approval.",
                amount  # This revenue would have been lost without pre-verification!
            )
        
        # Case 3: High/Critical risk without pre-verification - Decline
        return (
            TransactionStatus.DECLINED,
            False,
            f"Transaction declined - High risk detected (Score: {risk_score:.1f}/100). "
            f"Use pre-verification to enable instant approval for future purchases.",
            0.0
        )
    
    def get_merchant_analytics(
        self,
        merchant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[Dict]:
        merchant_txns = [
            record for record in self.transaction_history
            if record['transaction'].merchant_id == merchant_id
            and start_date <= record['timestamp'] <= end_date
        ]
        
        if not merchant_txns:
            return None
        
        total = len(merchant_txns)
        approved = sum(1 for r in merchant_txns if r['response'].approved)
        declined = sum(1 for r in merchant_txns if not r['response'].approved)
        pre_verified = sum(1 for r in merchant_txns if r['pre_verified'])
        
        # Calculate revenue saved (high-risk transactions that were pre-verified)
        revenue_saved = sum(
            r['response'].revenue_saved or 0
            for r in merchant_txns
        )
        
        # fraud prevented 
        fraud_prevented = sum(
            1 for r in merchant_txns
            if r['response'].status == TransactionStatus.DECLINED
            and r['response'].risk_assessment.risk_score >= 70
        )
        
        # average risk
        avg_risk = sum(
            r['response'].risk_assessment.risk_score
            for r in merchant_txns
        ) / total if total > 0 else 0
        
        return {
            'merchant_id': merchant_id,
            'period_start': start_date,
            'period_end': end_date,
            'total_transactions': total,
            'total_approved': approved,
            'total_declined': declined,
            'total_pre_verified': pre_verified,
            'fraud_prevented_count': fraud_prevented,
            'revenue_saved': revenue_saved,
            'approval_rate': (approved / total * 100) if total > 0 else 0,
            'avg_risk_score': avg_risk
        }
    
    def get_transaction_history(self, limit: int = 50) -> list:
        recent = self.transaction_history[-limit:]
        return [
            {
                'transaction_id': record['transaction'].transaction_id,
                'merchant_id': record['transaction'].merchant_id,
                'customer_id': record['transaction'].customer_id,
                'amount': record['transaction'].amount,
                'risk_score': record['response'].risk_assessment.risk_score,
                'risk_level': record['response'].risk_assessment.risk_level,
                'approved': record['response'].approved,
                'pre_verified': record['pre_verified'],
                'revenue_saved': record['response'].revenue_saved,
                'timestamp': record['timestamp'].isoformat()
            }
            for record in recent
        ]
