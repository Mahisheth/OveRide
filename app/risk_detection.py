import random
from datetime import datetime, timedelta
from typing import Dict, List
from app.model import Transaction, RiskAssessment, RiskLevel

class RiskEngine:
    def __init__(self):
        self.velocity_tracker: Dict[str, List[datetime]] = {}
        self.known_devices: Dict[str, set] = {}
    
    def calculate_risk_score(self, transaction: Transaction) -> RiskAssessment:
        risk_factors = []
        total_risk_score = 0.0
        
        # Transaction Amount
        amount_risk = self._assess_amount_risk(transaction.amount)
        total_risk_score += amount_risk
        if amount_risk > 15:
            risk_factors.append(f"High transaction amount: ${transaction.amount:.2f}")
        
        # Velocity: multiple transactions in a short time 
        velocity_risk = self._assess_velocity(transaction.customer_id)
        total_risk_score += velocity_risk
        if velocity_risk > 10:
            risk_factors.append("Multiple transactions in short timeframe")
        
        # Geographic Mismatch
        if transaction.billing_zip and transaction.shipping_zip:
            geo_risk = self._assess_geographic_mismatch(
                transaction.billing_zip,
                transaction.shipping_zip
            )
            total_risk_score += geo_risk
            if geo_risk > 10:
                risk_factors.append("Billing and shipping address mismatch")
        
        # Device Fingerprint
        if transaction.device_fingerprint:
            device_risk = self._assess_device_risk(
                transaction.customer_id,
                transaction.device_fingerprint
            )
            total_risk_score += device_risk
            if device_risk > 15:
                risk_factors.append("Transaction from new or suspicious device")
        
        # Time-based Patterns
        time_risk = self._assess_time_patterns(transaction.timestamp)
        total_risk_score += time_risk
        if time_risk > 10:
            risk_factors.append("Transaction at unusual time")
        
        # Cap the score at 100
        total_risk_score = min(100.0, total_risk_score)
        
        # categorical risk level
        risk_level = self._categorize_risk_level(total_risk_score)
        
        # confidence (more factors = higher confidence)
        confidence = self._calculate_confidence(len(risk_factors))
        
        is_fraud = total_risk_score >= 70
        fraud_prob = total_risk_score / 100

        return RiskAssessment(
            risk_score=total_risk_score,
            risk_level=risk_level,
            risk_factors=risk_factors,
            confidence=confidence,
            is_fraud=is_fraud,
            fraud_prob=fraud_prob
        )
    # risk assessment
    def _assess_amount_risk(self, amount: float) -> float:
        if amount < 50:
            return 5.0
        elif amount < 200:
            return 10.0
        elif amount < 500:
            return 20.0
        elif amount < 1000:
            return 30.0
        else:
            # Very high amounts
            return 40.0
    # velocity assessment
    def _assess_velocity(self, customer_id: str) -> float:
        now = datetime.now()
        
        # Initialize tracking for new customers
        if customer_id not in self.velocity_tracker:
            self.velocity_tracker[customer_id] = []

        self.velocity_tracker[customer_id] = [
            ts for ts in self.velocity_tracker[customer_id]
            if now - ts < timedelta(hours=1)
        ]
        
        # Count recent transactions
        recent_count = len(self.velocity_tracker[customer_id])
        
        # Add this transaction to the tracker
        self.velocity_tracker[customer_id].append(now)
        
        #  velocity risk
        if recent_count >= 5:
            return 35.0  # Very high velocity
        elif recent_count >= 3:
            return 20.0  # High velocity
        elif recent_count >= 2:
            return 10.0  # Moderate velocity
        else:
            return 0.0   # Normal
    
    def _assess_geographic_mismatch(self, billing_zip: str, shipping_zip: str) -> float:
        if billing_zip[:3] != shipping_zip[:3]:
            return 15.0
        return 0.0
    
    def _assess_device_risk(self, customer_id: str, device_fingerprint: str) -> float:
        # Initialize known devices for new customers
        if customer_id not in self.known_devices:
            self.known_devices[customer_id] = set()
        
        # Checking if device is known
        if device_fingerprint in self.known_devices[customer_id]:
            return 0.0  # Known device = low risk
        
        # New device detected
        # Add to known devices for future
        self.known_devices[customer_id].add(device_fingerprint)
        
        # For simulation: 30% of new devices are flagged as high risk
        if random.random() > 0.7:
            return 20.0  # Suspicious new device
        else:
            return 10.0  # New but not suspicious
    
    def _assess_time_patterns(self, timestamp: datetime) -> float:
        # flagging trasactions at unusual hours 
        hour = timestamp.hour
        
        # Suspicious hours: 2 AM - 6 AM
        if 2 <= hour <= 6:
            return 15.0
        # Somewhat unusual: 11 PM - 2 AM or 6 AM - 7 AM
        elif hour >= 23 or hour <= 7:
            return 5.0
        else:
            return 0.0
    
    def _categorize_risk_level(self, risk_score: float) -> RiskLevel:
        # converting numeric score to categorical level
        if risk_score >= 70:
            return RiskLevel.CRITICAL
        elif risk_score >= 50:
            return RiskLevel.HIGH
        elif risk_score >= 30:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _calculate_confidence(self, num_factors: int) -> float:
       # confidence in risk scores
        base_confidence = 0.5
        factor_boost = num_factors * 0.08
        return min(0.95, base_confidence + factor_boost)
