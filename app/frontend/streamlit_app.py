import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import streamlit as st
import uuid
from datetime import datetime

from app.authorize import AuthorizationEngine
from app.model import (
    Transaction,
    AuthorizationRequest,
    PreVerificationRequest
)
# -----------------------------------
# Initialize Engine (Simulated Backend)
# -----------------------------------
if "engine" not in st.session_state:
    st.session_state.engine = AuthorizationEngine()

engine = st.session_state.engine

st.set_page_config(
    page_title="OveRide - Proactive Fraud Protection",
    layout="centered"
)

st.title("🚀 OveRide")
st.subheader("Reimagining Payments with Pre-Approved Transactions")

st.markdown("---")

# ==========================================
# INPUT SECTION
# ==========================================
st.header("🛒 Simulate a Purchase")

customer_id = st.selectbox(
    "Customer ID",
    ["cust_001", "cust_002"]
)

merchant_id = st.text_input("Merchant ID", "merchant_123")

amount = st.number_input(
    "Transaction Amount ($)",
    min_value=1.0,
    value=5000.0
)

col1, col2 = st.columns(2)

# ==========================================
# PRE-VERIFY BUTTON
# ==========================================
with col1:
    if st.button("🔐 Pre-Verify Purchase"):

        preverify_request = PreVerificationRequest(
            customer_id=customer_id,
            amount=amount
        )

        response = engine.pre_verify_transaction(preverify_request)

        st.session_state.verification_token = response.verification_token

        st.success("Pre-verification successful!")
        st.info(f"Verification Token: {response.verification_token}")
        st.info(f"Expires at: {response.expires_at}")

# ==========================================
# AUTHORIZE BUTTON
# ==========================================
with col2:
    if st.button("💳 Authorize Transaction"):

        transaction = Transaction(
            transaction_id=str(uuid.uuid4()),
            customer_id=customer_id,
            merchant_id=merchant_id,
            amount=amount,
            timestamp=datetime.utcnow()
        )

        auth_request = AuthorizationRequest(
            transaction=transaction,
            customer_verification_token=st.session_state.get("verification_token")
        )

        response = engine.authorize_transaction(auth_request)

        st.markdown("---")
        st.subheader("📊 Authorization Result")

        st.write(f"**Status:** {response.status}")
        st.write(f"**Approved:** {response.approved}")
        st.write(f"**Risk Score:** {response.risk_assessment.risk_score}")
        st.write(f"**Risk Level:** {response.risk_assessment.risk_level}")
        st.write(f"**Message:** {response.message}")
        st.write(f"**Processing Time:** {response.processing_time_ms:.2f} ms")
        st.write(f"**Revenue Saved:** ${response.revenue_saved}")