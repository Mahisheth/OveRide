import sys
import os
import requests
import streamlit as st
import uuid
from datetime import datetime

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.repository.transaction import TransactionRepository

# ---------------------------
# CONFIG
# ---------------------------

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="OveRide - Proactive Fraud Protection",
    layout="centered"
)

st.title("OveRide")
st.subheader("Reimagining Payments with Pre-Approved Transactions")
st.markdown("---")

repo = TransactionRepository()


# ---------------------------
# FETCH REAL DATA FROM DB
# ---------------------------

customers = repo.get_unique_customers()
merchants = repo.get_unique_merchants()


# ---------------------------
# TABS
# ---------------------------

tab1, tab2, tab3 = st.tabs([
    "Customer",
    "Merchant Dashboard",
    "Bank Monitoring"
])


# ===========================
# CUSTOMER TAB
# ===========================

with tab1:

    st.header("Simulate a Purchase")

    if not customers:
        st.warning("No customers found in database.")
        st.stop()

    customer_id = st.selectbox("Customer ID", customers)

    if merchants:
        merchant_id = st.selectbox("Merchant ID", merchants)
    else:
        merchant_id = st.text_input("Merchant ID")

    amount = st.number_input(
        "Transaction Amount ($)",
        min_value=1.0,
        value=500.0
    )

    col1, col2 = st.columns(2)

    # ---------------------------
    # PRE-VERIFY
    # ---------------------------
    with col1:
        if st.button("Pre-Verify Purchase"):

            payload = {
                "customer_id": customer_id,
                "amount": amount
            }

            response = requests.post(
                f"{API_BASE_URL}/pre-verify",
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                st.session_state.verification_token = data["verification_token"]

                st.success("Pre-verification successful!")
                st.info(f"Verification Token: {data['verification_token']}")
                st.info(f"Expires at: {data['expires_at']}")
            else:
                st.error("Pre-verification failed.")

    # ---------------------------
    # AUTHORIZE
    # ---------------------------
    with col2:
        if st.button("Authorize Transaction"):

            transaction_payload = {
                "transaction": {
                    "transaction_id": str(uuid.uuid4()),
                    "customer_id": customer_id,
                    "merchant_id": merchant_id,
                    "amount": amount,
                    "timestamp": datetime.utcnow().isoformat()
                },
                "customer_verification_token": st.session_state.get("verification_token")
            }

            response = requests.post(
                f"{API_BASE_URL}/authorize",
                json=transaction_payload
            )

            if response.status_code == 200:
                data = response.json()

                st.markdown("---")
                st.subheader("Authorization Result")

                st.write(f"**Status:** {data['status']}")
                st.write(f"**Approved:** {data['approved']}")
                st.write(f"**Risk Score:** {data['risk_assessment']['risk_score']}")
                st.write(f"**Risk Level:** {data['risk_assessment']['risk_level']}")
                st.write(f"**Message:** {data['message']}")
                st.write(f"**Processing Time:** {data['processing_time_ms']:.2f} ms")
                st.write(f"**Revenue Saved:** ${data['revenue_saved']}")
            else:
                st.error("Authorization failed. Is the Bank API running?")


# ===========================
# MERCHANT DASHBOARD
# ===========================

with tab2:

    st.header("Merchant Revenue Insights")

    transactions = repo.get_all_transactions()

    total_transactions = len(transactions)
    approved_transactions = [t for t in transactions if t["approved"] == 1]

    approval_rate = (
        (len(approved_transactions) / total_transactions) * 100
        if total_transactions > 0 else 0
    )

    total_revenue = sum(t["amount"] for t in approved_transactions)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Transactions", total_transactions)
    col2.metric("Approval Rate", f"{approval_rate:.2f}%")
    col3.metric("Approved Revenue", f"${total_revenue:,.2f}")

    st.markdown("---")
    st.subheader("Transaction History")

    if transactions:
        st.dataframe(transactions)
    else:
        st.info("No transactions yet.")


# # ===========================
# # BANK MONITORING DASHBOARD
# # ===========================

# with tab3:

#     st.header("Risk Monitoring Dashboard")

#     transactions = repo.get_all_transactions()

#     if transactions:

#         high_risk = [t for t in transactions if t["risk_level"] == "HIGH"]
#         medium_risk = [t for t in transactions if t["risk_level"] == "MEDIUM"]
#         low_risk = [t for t in transactions if t["risk_level"] == "LOW"]

#         col1, col2, col3 = st.columns(3)
#         col1.metric("High Risk", len(high_risk))
#         col2.metric("Medium Risk", len(medium_risk))
#         col3.metric("Low Risk", len(low_risk))

#         st.markdown("---")
#         st.dataframe(transactions)

#     else:
#         st.info("No transactions recorded yet.")