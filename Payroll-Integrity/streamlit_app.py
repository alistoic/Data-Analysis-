import streamlit as st
import pandas as pd
import plotly.express as px
import joblib

# Page config
st.set_page_config(page_title="Payroll Anomaly Detector", layout="wide")
st.title("🚨 Automated Payroll Anomaly & Fraud Detector")
st.markdown("Detects ghost employees and calculation errors before payroll is processed.")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('data/payroll_with_anomalies.csv')
    # Convert columns to appropriate types
    df['pay_period'] = pd.to_datetime(df['pay_period'])
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
dept_filter = st.sidebar.multiselect(
    "Department",
    options=sorted(df['dept_name'].dropna().unique()),
    default=sorted(df['dept_name'].dropna().unique())
)
anomaly_filter = st.sidebar.radio(
    "Show only anomalies?",
    options=["All", "Anomalies Only"]
)

# Apply filters
filtered_df = df[df['dept_name'].isin(dept_filter)]
if anomaly_filter == "Anomalies Only":
    filtered_df = filtered_df[filtered_df['anomaly_score'] == 1]

# ------------------------------
# KPIs
# ------------------------------
col1, col2, col3, col4 = st.columns(4)
total_employees = filtered_df['employee_id'].nunique()
total_payroll = filtered_df['gross_pay'].sum()
anomaly_count = filtered_df['anomaly_score'].sum()
error_rate = (anomaly_count / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0

col1.metric("👥 Employees", f"{total_employees:,}")
col2.metric("💰 Total Gross Pay", f"${total_payroll:,.2f}")
col3.metric("⚠️ Anomalies", f"{anomaly_count:,}")
col4.metric("📊 Error Rate", f"{error_rate:.2f}%")

# ------------------------------
# Anomaly Details Table
# ------------------------------
st.subheader("🔍 Anomalous Payroll Records")
anomaly_table = filtered_df[filtered_df['anomaly_score'] == 1][
    ['payroll_id', 'employee_id', 'first_name', 'last_name', 'dept_name',
     'gross_pay', 'deductions', 'net_pay', 'overtime_hours', 'anomaly_decision']
].sort_values('anomaly_decision', ascending=True)
st.dataframe(anomaly_table, width='stretch')

# ------------------------------
# Visualizations
# ------------------------------
st.subheader("📊 Insights")
tab1, tab2, tab3 = st.tabs(["Gross vs Net", "Anomaly Distribution", "Department Breakdown"])
"""
with tab1:
    fig = px.scatter(filtered_df, x='gross_pay', y='net_pay', color='anomaly_score',
                     hover_data=['employee_id', 'first_name', 'last_name'],
                     title="Gross Pay vs Net Pay (Red = Anomaly)")
    st.plotly_chart(fig, width='stretch')
""" 
with tab1:
    # Convert anomaly_score to string/category for discrete color mapping
    filtered_df['anomaly_type'] = filtered_df['anomaly_score'].map({0: 'Normal', 1: 'Anomaly'})
    
    fig = px.scatter(filtered_df, x='gross_pay', y='net_pay', 
                     color='anomaly_type',
                     color_discrete_map={'Normal': 'light', 'Anomaly': 'red'},
                     hover_data=['employee_id', 'first_name', 'last_name'],
                     title="Gross Pay vs Net Pay (Red = Anomaly)")
    st.plotly_chart(fig, width='stretch')

with tab2:
    fig2 = px.histogram(filtered_df, x='anomaly_decision', nbins=50,
                        title="Distribution of Anomaly Decision Scores")
    st.plotly_chart(fig2, width='stretch')

with tab3:
    dept_anomalies = filtered_df.groupby('dept_name')['anomaly_score'].sum().reset_index()
    fig3 = px.bar(dept_anomalies, x='dept_name', y='anomaly_score',
                  title="Anomalies by Department")
    st.plotly_chart(fig3, width='stretch')

# ------------------------------
# SQL Quality Checks (simulated)
# ------------------------------
st.subheader("📋 SQL Data Quality Checks")
st.code("""
-- Example: missing SSN
SELECT employee_id, first_name, last_name
FROM employees
WHERE ssn IS NULL;
""", language='sql')
missing_ssn = df[df['ssn'].isna()][['employee_id', 'first_name', 'last_name']]
if not missing_ssn.empty:
    st.warning("Employees with missing SSN:")
    st.dataframe(missing_ssn)
else:
    st.success("No missing SSNs found.")