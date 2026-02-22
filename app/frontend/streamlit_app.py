import sys
import os
import requests
import streamlit as st
import uuid
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from collections import Counter

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.repository.transaction import TransactionRepository

# ---------------------------
# CONFIG
# ---------------------------

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="OveRide - Proactive Fraud Protection",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "OveRide - Reimagining Payments with Pre-Approved Transactions"
    }
)

# ---------------------------
# CUSTOM CSS
# ---------------------------

st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
        --background: #0f172a;
        --surface: #1e293b;
        --text-primary: #f1f5f9;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.3);
    }
    
    .main-header h1 {
        color: white;
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.3);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #6366f1;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: rgba(241, 245, 249, 0.7);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.5rem;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.375rem 0.75rem;
        border-radius: 0.5rem;
        font-weight: 600;
        font-size: 0.875rem;
        margin: 0.25rem;
    }
    
    .badge-success {
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    
    .badge-warning {
        background: rgba(245, 158, 11, 0.2);
        color: #f59e0b;
        border: 1px solid rgba(245, 158, 11, 0.4);
    }
    
    .badge-danger {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }
    
    .badge-info {
        background: rgba(99, 102, 241, 0.2);
        color: #6366f1;
        border: 1px solid rgba(99, 102, 241, 0.4);
    }
    
    /* Result card */
    .result-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 2rem;
        border-radius: 1rem;
        border: 2px solid rgba(99, 102, 241, 0.3);
        margin: 1.5rem 0;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }
    
    .result-approved {
        border-color: rgba(16, 185, 129, 0.5);
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%);
    }
    
    .result-declined {
        border-color: rgba(239, 68, 68, 0.5);
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%);
    }
    
    /* Transaction form */
    .transaction-form {
        background: #1e293b;
        padding: 2rem;
        border-radius: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Info box */
    .info-box {
        background: rgba(99, 102, 241, 0.1);
        border-left: 4px solid #6366f1;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    
    .success-box {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10b981;
    }
    
    .warning-box {
        background: rgba(245, 158, 11, 0.1);
        border-left: 4px solid #f59e0b;
    }
    
    .error-box {
        background: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #ef4444;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        background-color: rgba(30, 41, 59, 0.5);
        border-radius: 0.5rem;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        border-radius: 0.5rem;
        transition: all 0.3s;
        border: none;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# HEADER
# ---------------------------

st.markdown("""
<div class="main-header">
    <h1>🛡️ OveRide</h1>
    <p>Reimagining Payments with Pre-Approved Transactions</p>
</div>
""", unsafe_allow_html=True)

repo = TransactionRepository()

# Initialize session state
if 'verification_token' not in st.session_state:
    st.session_state.verification_token = None
if 'last_transaction' not in st.session_state:
    st.session_state.last_transaction = None

# ---------------------------
# FETCH REAL DATA FROM DB
# ---------------------------

try:
    customers = repo.get_unique_customers()
    merchants = repo.get_unique_merchants()
    all_transactions = repo.get_all_transactions()
except Exception as e:
    st.error(f"⚠️ Database connection error: {str(e)}")
    st.stop()


# ---------------------------
# SIDEBAR
# ---------------------------

with st.sidebar:
    st.markdown("### 📊 System Overview")
    
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=2)
        if response.status_code == 200:
            st.success("✅ API Connected")
        else:
            st.error("⚠️ API Error")
    except:
        st.error("❌ API Offline")
    
    st.markdown("---")
    st.markdown(f"**Total Customers:** {len(customers)}")
    st.markdown(f"**Total Merchants:** {len(merchants)}")
    st.markdown(f"**Total Transactions:** {len(all_transactions)}")
    
    st.markdown("---")
    st.markdown("### 💡 How It Works")
    st.markdown("""
    1. **Pre-Verify** high-risk transactions
    2. Receive a verification token
    3. **Authorize** with the token
    4. Enjoy instant approval
    """)


# ---------------------------
# TABS
# ---------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "🛒 Customer Portal",
    "📈 Merchant Dashboard",
    "🔍 Risk Monitoring",
    "📊 Analytics"
])


# ===========================
# TAB 1: CUSTOMER PORTAL
# ===========================

with tab1:
    
    col_form, col_status = st.columns([1, 1])
    
    with col_form:
        st.markdown("### 💳 New Transaction")
        
        if not customers:
            st.warning("⚠️ No customers found in database.")
            st.stop()
        
        with st.container():
            customer_id = st.selectbox(
                "👤 Customer ID",
                customers,
                help="Select your customer ID"
            )
            
            if merchants:
                merchant_id = st.selectbox(
                    "🏪 Merchant",
                    merchants,
                    help="Select the merchant"
                )
            else:
                merchant_id = st.text_input("🏪 Merchant ID")
            
            amount = st.number_input(
                "💵 Transaction Amount ($)",
                min_value=1.0,
                max_value=100000.0,
                value=500.0,
                step=50.0,
                help="Enter the transaction amount"
            )
        
        st.markdown("---")
        
        # Pre-verify button
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🔐 Pre-Verify Purchase", use_container_width=True):
                with st.spinner("Verifying..."):
                    payload = {
                        "customer_id": customer_id,
                        "amount": amount
                    }
                    
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/pre-verify",
                            json=payload,
                            timeout=5
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            if data.get("verified"):
                                st.session_state.verification_token = data["verification_token"]
                                st.success("✅ Pre-verification successful!")
                                st.info(f"🔑 Token: `{data['verification_token'][:20]}...`")
                                st.info(f"⏰ Expires: {data['expires_at']}")
                            else:
                                st.error(f"❌ {data.get('message', 'Pre-verification denied')}")
                                st.session_state.verification_token = None
                        else:
                            st.error("❌ Pre-verification request failed")
                            st.session_state.verification_token = None
                    except Exception as e:
                        st.error(f"⚠️ Connection error: {str(e)}")
        
        with col_btn2:
            authorize_disabled = False
            if st.button("✅ Authorize Transaction", use_container_width=True, disabled=authorize_disabled):
                with st.spinner("Processing authorization..."):
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
                    
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/authorize",
                            json=transaction_payload,
                            timeout=5
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.last_transaction = data
                            st.rerun()
                        else:
                            st.error("❌ Authorization failed. Is the API running?")
                    except Exception as e:
                        st.error(f"⚠️ Connection error: {str(e)}")
    
    with col_status:
        st.markdown("### 📋 Transaction Status")
        
        if st.session_state.verification_token:
            st.markdown("""
            <div class="success-box">
                <strong>🔐 Pre-Verification Active</strong><br/>
                You have an active verification token. Proceed with authorization for instant approval.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="info-box">
                <strong>ℹ️ No Active Pre-Verification</strong><br/>
                Pre-verify high-risk transactions for guaranteed approval.
            </div>
            """, unsafe_allow_html=True)
        
        if st.session_state.last_transaction:
            data = st.session_state.last_transaction
            
            # Determine status styling
            if data['approved']:
                result_class = "result-card result-approved"
                status_icon = "✅"
                status_text = "APPROVED"
            else:
                result_class = "result-card result-declined"
                status_icon = "❌"
                status_text = "DECLINED"
            
            # Risk level badge
            risk_level = data['risk_assessment']['risk_level'].upper()
            if risk_level in ['HIGH', 'CRITICAL']:
                risk_badge = f'<span class="status-badge badge-danger">🔴 {risk_level}</span>'
            elif risk_level == 'MEDIUM':
                risk_badge = f'<span class="status-badge badge-warning">🟡 {risk_level}</span>'
            else:
                risk_badge = f'<span class="status-badge badge-success">🟢 {risk_level}</span>'
            
            st.markdown(f"""
            <div class="{result_class}">
                <h2>{status_icon} {status_text}</h2>
                <hr style="border-color: rgba(255,255,255,0.1); margin: 1rem 0;"/>
                <p><strong>Transaction ID:</strong> {data['transaction_id'][:16]}...</p>
                <p><strong>Status:</strong> <span class="status-badge badge-info">{data['status'].upper()}</span></p>
                <p><strong>Risk Score:</strong> {data['risk_assessment']['risk_score']:.1f}/100</p>
                <p><strong>Risk Level:</strong> {risk_badge}</p>
                <p><strong>Message:</strong> {data['message']}</p>
                <p><strong>Processing Time:</strong> {data['processing_time_ms']:.2f} ms</p>
                <p><strong>Revenue Saved:</strong> <span style="color: #10b981; font-weight: 700;">${data['revenue_saved']:.2f}</span></p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔄 Clear Result"):
                st.session_state.last_transaction = None
                st.session_state.verification_token = None
                st.rerun()


# ===========================
# TAB 2: MERCHANT DASHBOARD
# ===========================

with tab2:
    st.markdown("### 📊 Merchant Revenue Insights")
    
    transactions = all_transactions
    
    if transactions:
        # Calculate metrics
        total_transactions = len(transactions)
        approved_transactions = [t for t in transactions if t.get("approved") == 1]
        declined_transactions = [t for t in transactions if t.get("approved") == 0]
        pre_verified = [t for t in transactions if t.get("status") == "pre_verified"]
        
        approval_rate = (len(approved_transactions) / total_transactions * 100) if total_transactions > 0 else 0
        total_revenue = sum(t.get("amount", 0) for t in approved_transactions)
        total_saved = sum(t.get("revenue_saved", 0) for t in transactions)
        avg_transaction = total_revenue / len(approved_transactions) if approved_transactions else 0
        
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_transactions:,}</div>
                <div class="metric-label">Total Transactions</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #10b981;">{approval_rate:.1f}%</div>
                <div class="metric-label">Approval Rate</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #6366f1;">${total_revenue:,.0f}</div>
                <div class="metric-label">Total Revenue</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #10b981;">${total_saved:,.0f}</div>
                <div class="metric-label">Revenue Saved</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br/>", unsafe_allow_html=True)
        
        # Charts
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # Transaction status pie chart
            status_data = pd.DataFrame({
                'Status': ['Approved', 'Declined'],
                'Count': [len(approved_transactions), len(declined_transactions)]
            })
            
            fig_status = px.pie(
                status_data,
                values='Count',
                names='Status',
                title='Transaction Status Distribution',
                color='Status',
                color_discrete_map={'Approved': '#10b981', 'Declined': '#ef4444'},
                hole=0.4
            )
            fig_status.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f1f5f9')
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col_chart2:
            # Risk level distribution
            risk_levels = [t.get("risk_level", "unknown") for t in transactions]
            risk_counter = Counter(risk_levels)
            
            risk_data = pd.DataFrame({
                'Risk Level': list(risk_counter.keys()),
                'Count': list(risk_counter.values())
            })
            
            color_map = {
                'low': '#10b981',
                'medium': '#f59e0b',
                'high': '#ef4444',
                'critical': '#dc2626'
            }
            
            fig_risk = px.bar(
                risk_data,
                x='Risk Level',
                y='Count',
                title='Risk Level Distribution',
                color='Risk Level',
                color_discrete_map=color_map
            )
            fig_risk.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f1f5f9'),
                showlegend=False
            )
            st.plotly_chart(fig_risk, use_container_width=True)
        
        st.markdown("---")
        
        # Recent transactions
        st.markdown("### 📜 Recent Transactions")
        
        # Prepare dataframe
        df = pd.DataFrame(transactions)
        if not df.empty:
            # Select and format columns
            display_cols = []
            if 'timestamp' in df.columns:
                display_cols.append('timestamp')
            if 'customer_id' in df.columns:
                display_cols.append('customer_id')
            if 'merchant_id' in df.columns:
                display_cols.append('merchant_id')
            if 'amount' in df.columns:
                display_cols.append('amount')
            if 'risk_score' in df.columns:
                display_cols.append('risk_score')
            if 'risk_level' in df.columns:
                display_cols.append('risk_level')
            if 'approved' in df.columns:
                display_cols.append('approved')
            if 'revenue_saved' in df.columns:
                display_cols.append('revenue_saved')
            
            df_display = df[display_cols].head(50)
            
            # Format columns
            if 'amount' in df_display.columns:
                df_display['amount'] = df_display['amount'].apply(lambda x: f"${x:,.2f}")
            if 'revenue_saved' in df_display.columns:
                df_display['revenue_saved'] = df_display['revenue_saved'].apply(lambda x: f"${x:,.2f}")
            if 'risk_score' in df_display.columns:
                df_display['risk_score'] = df_display['risk_score'].apply(lambda x: f"{x:.1f}")
            if 'approved' in df_display.columns:
                df_display['approved'] = df_display['approved'].apply(lambda x: "✅" if x == 1 else "❌")
            
            st.dataframe(df_display, use_container_width=True, height=400)
    else:
        st.info("📭 No transactions yet. Start by processing some transactions in the Customer Portal.")


# ===========================
# TAB 3: RISK MONITORING
# ===========================

with tab3:
    st.markdown("### 🔍 Risk Monitoring Dashboard")
    
    transactions = all_transactions
    
    if transactions:
        # Risk metrics
        high_risk = [t for t in transactions if t.get("risk_level") in ["high", "critical"]]
        medium_risk = [t for t in transactions if t.get("risk_level") == "medium"]
        low_risk = [t for t in transactions if t.get("risk_level") == "low"]
        
        fraud_detected = [t for t in transactions if t.get("is_fraud")]
        fraud_prevented = [t for t in fraud_detected if t.get("approved") == 0]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #ef4444;">{len(high_risk)}</div>
                <div class="metric-label">High Risk Transactions</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #f59e0b;">{len(medium_risk)}</div>
                <div class="metric-label">Medium Risk</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #10b981;">{len(low_risk)}</div>
                <div class="metric-label">Low Risk</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #6366f1;">{len(fraud_prevented)}</div>
                <div class="metric-label">Fraud Prevented</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br/>", unsafe_allow_html=True)
        
        # Risk score distribution
        col_hist, col_scatter = st.columns(2)
        
        with col_hist:
            risk_scores = [t.get("risk_score", 0) for t in transactions]
            
            fig_hist = go.Figure(data=[go.Histogram(
                x=risk_scores,
                nbinsx=20,
                marker_color='#6366f1',
                opacity=0.8
            )])
            
            fig_hist.update_layout(
                title='Risk Score Distribution',
                xaxis_title='Risk Score',
                yaxis_title='Count',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f1f5f9')
            )
            
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col_scatter:
            # Amount vs Risk Score
            df_scatter = pd.DataFrame(transactions)
            if 'amount' in df_scatter.columns and 'risk_score' in df_scatter.columns:
                fig_scatter = px.scatter(
                    df_scatter,
                    x='amount',
                    y='risk_score',
                    color='approved',
                    title='Transaction Amount vs Risk Score',
                    labels={'amount': 'Amount ($)', 'risk_score': 'Risk Score', 'approved': 'Approved'},
                    color_discrete_map={1: '#10b981', 0: '#ef4444'},
                    opacity=0.7
                )
                
                fig_scatter.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#f1f5f9')
                )
                
                st.plotly_chart(fig_scatter, use_container_width=True)
        
        st.markdown("---")
        
        # High-risk transactions table
        st.markdown("### ⚠️ High-Risk Transactions")
        
        if high_risk:
            df_high_risk = pd.DataFrame(high_risk)
            display_cols = []
            
            if 'timestamp' in df_high_risk.columns:
                display_cols.append('timestamp')
            if 'customer_id' in df_high_risk.columns:
                display_cols.append('customer_id')
            if 'amount' in df_high_risk.columns:
                display_cols.append('amount')
            if 'risk_score' in df_high_risk.columns:
                display_cols.append('risk_score')
            if 'risk_level' in df_high_risk.columns:
                display_cols.append('risk_level')
            if 'approved' in df_high_risk.columns:
                display_cols.append('approved')
            if 'status' in df_high_risk.columns:
                display_cols.append('status')
            
            df_display = df_high_risk[display_cols].head(20)
            
            if 'amount' in df_display.columns:
                df_display['amount'] = df_display['amount'].apply(lambda x: f"${x:,.2f}")
            if 'risk_score' in df_display.columns:
                df_display['risk_score'] = df_display['risk_score'].apply(lambda x: f"{x:.1f}")
            if 'approved' in df_display.columns:
                df_display['approved'] = df_display['approved'].apply(lambda x: "✅" if x == 1 else "❌")
            
            st.dataframe(df_display, use_container_width=True, height=300)
        else:
            st.success("✅ No high-risk transactions detected!")
    else:
        st.info("📭 No transaction data available for risk monitoring.")


# ===========================
# TAB 4: ANALYTICS
# ===========================

with tab4:
    st.markdown("### 📊 Advanced Analytics")
    
    transactions = all_transactions
    
    if transactions and len(transactions) > 0:
        df = pd.DataFrame(transactions)
        
        # Time-based analysis if timestamp exists
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df.dropna(subset=['timestamp'])
            
            if not df.empty:
                df['date'] = df['timestamp'].dt.date
                
                # Transactions over time
                daily_stats = df.groupby('date').agg({
                    'amount': ['sum', 'count'],
                    'approved': 'sum'
                }).reset_index()
                
                daily_stats.columns = ['date', 'total_amount', 'transaction_count', 'approved_count']
                
                fig_timeline = go.Figure()
                
                fig_timeline.add_trace(go.Scatter(
                    x=daily_stats['date'],
                    y=daily_stats['transaction_count'],
                    mode='lines+markers',
                    name='Total Transactions',
                    line=dict(color='#6366f1', width=3),
                    marker=dict(size=8)
                ))
                
                fig_timeline.add_trace(go.Scatter(
                    x=daily_stats['date'],
                    y=daily_stats['approved_count'],
                    mode='lines+markers',
                    name='Approved Transactions',
                    line=dict(color='#10b981', width=3),
                    marker=dict(size=8)
                ))
                
                fig_timeline.update_layout(
                    title='Transaction Trends Over Time',
                    xaxis_title='Date',
                    yaxis_title='Number of Transactions',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#f1f5f9'),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Top merchants and customers
        col_merchants, col_customers = st.columns(2)
        
        with col_merchants:
            if 'merchant_id' in df.columns and 'amount' in df.columns:
                merchant_revenue = df[df['approved'] == 1].groupby('merchant_id')['amount'].sum().sort_values(ascending=False).head(10)
                
                fig_merchants = go.Figure(data=[go.Bar(
                    x=merchant_revenue.values,
                    y=merchant_revenue.index,
                    orientation='h',
                    marker_color='#6366f1',
                    text=[f"${v:,.0f}" for v in merchant_revenue.values],
                    textposition='auto'
                )])
                
                fig_merchants.update_layout(
                    title='Top 10 Merchants by Revenue',
                    xaxis_title='Revenue ($)',
                    yaxis_title='Merchant ID',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#f1f5f9'),
                    height=400
                )
                
                st.plotly_chart(fig_merchants, use_container_width=True)
        
        with col_customers:
            if 'customer_id' in df.columns and 'amount' in df.columns:
                customer_spending = df[df['approved'] == 1].groupby('customer_id')['amount'].sum().sort_values(ascending=False).head(10)
                
                fig_customers = go.Figure(data=[go.Bar(
                    x=customer_spending.values,
                    y=customer_spending.index,
                    orientation='h',
                    marker_color='#8b5cf6',
                    text=[f"${v:,.0f}" for v in customer_spending.values],
                    textposition='auto'
                )])
                
                fig_customers.update_layout(
                    title='Top 10 Customers by Spending',
                    xaxis_title='Total Spending ($)',
                    yaxis_title='Customer ID',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#f1f5f9'),
                    height=400
                )
                
                st.plotly_chart(fig_customers, use_container_width=True)
        
        st.markdown("---")
        
        # Summary statistics
        st.markdown("### 📈 Summary Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_amount = df['amount'].mean() if 'amount' in df.columns else 0
            st.metric("Average Transaction", f"${avg_amount:,.2f}")
            
            max_amount = df['amount'].max() if 'amount' in df.columns else 0
            st.metric("Largest Transaction", f"${max_amount:,.2f}")
        
        with col2:
            avg_risk = df['risk_score'].mean() if 'risk_score' in df.columns else 0
            st.metric("Average Risk Score", f"{avg_risk:.1f}")
            
            if 'fraud_prob' in df.columns:
                avg_fraud_prob = df['fraud_prob'].mean() * 100
                st.metric("Avg Fraud Probability", f"{avg_fraud_prob:.1f}%")
        
        with col3:
            if 'revenue_saved' in df.columns:
                total_saved = df['revenue_saved'].sum()
                st.metric("Total Revenue Saved", f"${total_saved:,.2f}")
            
            pre_verified_count = len(df[df['status'] == 'pre_verified']) if 'status' in df.columns else 0
            st.metric("Pre-Verified Transactions", pre_verified_count)
    
    else:
        st.info("📭 Insufficient data for analytics. Process more transactions to see insights.")