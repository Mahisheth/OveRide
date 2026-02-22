from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DECLINED = "declined"
    PRE_VERIFIED = "pre_verified"  # High-risk but approved via pre-verification


class Transaction(BaseModel):
    transaction_id: str
    customer_id: str
    merchant_id: str
    amount: float = Field(gt=0, description="Transaction amount in USD")
    currency: str = "USD"
    last_four: str
    card_company: str
    billing_zip: Optional[str] = None
    shipping_zip: Optional[str] = None
    device_fingerprint: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "txn_123abc",
                "customer_id": "cust_456",
                "merchant_id": "merch_789",
                "amount": 299.99,
                "currency": "USD",
                "last_four": "4242",
                "card_company": "Visa"
            }
        }


class RiskAssessment(BaseModel):
    risk_score: float = Field(
        ge=0, 
        le=100, 
        description="Numeric risk score from 0 (lowest risk) to 100 (highest risk)"
    )
    risk_level: RiskLevel
    risk_factors: List[str] = Field(
        default_factory=list,
        description="List of specific risk factors detected"
    )
    confidence: float = Field(
        ge=0, 
        le=1,
        description="Confidence in the risk assessment (0-1)"
    )
    is_fraud: bool
    fraud_prob: float = Field(
        ge=0, 
        le=1,)

    class Config:
        json_schema_extra = {
            "example": {
                "risk_score": 65.0,
                "risk_level": "high",
                "risk_factors": [
                    "High transaction amount: $1500.00",
                    "Transaction from new device"
                ],
                "confidence": 0.82
            }
        }
# class RiskFactor(BaseModel):
#     code: str
#     description: str
#     weight: float


class AuthorizationRequest(BaseModel):
    """Request to authorize a transaction"""
    transaction: Transaction
    pre_verified: bool = False


class AuthorizationResponse(BaseModel):
    """
    Response from authorization attempt.
    Includes decision, risk assessment, and revenue impact.
    """
    transaction_id: str
    status: TransactionStatus
    approved: bool
    risk_assessment: RiskAssessment
    message: str
    processing_time_ms: float
    revenue_saved: float = 0.0
    
    # Key metric: Revenue saved from pre-verified high-risk transactions
    revenue_saved: float = Field(
        0.0,
        description="Amount of revenue saved by approving via pre-verification"
    )


class PreVerificationRequest(BaseModel):
    """Request to pre-verify a customer for a high-risk transaction"""
    customer_id: str
    merchant_id: str
    amount: float
    verification_method: str = Field(
        description="Verification method: SMS, email, biometric, etc."
    )


class PreVerificationResponse(BaseModel):
    """Response from pre-verification attempt"""
    verification_token: str
    expires_at: datetime
    verified: bool
    message: Optional[str] = None


class MerchantAnalytics(BaseModel):
    """
    Analytics dashboard data for merchants.
    Shows the business value of the pre-verification system.
    """
    merchant_id: str
    period_start: datetime
    period_end: datetime
    
    # Transaction counts
    total_transactions: int
    total_approved: int
    total_declined: int
    total_pre_verified: int
    
    # Key metrics
    fraud_prevented_count: int
    revenue_saved: float = Field(
        description="Total revenue saved from pre-verified high-risk transactions"
    )
    approval_rate: float = Field(description="Percentage of approved transactions")
    avg_risk_score: float
