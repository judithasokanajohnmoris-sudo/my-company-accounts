import streamlit as st
import pandas as pd
from datetime import date
import os

# --- SETTINGS ---
FILE_NAME = "my_accounts.csv"

st.set_page_config(page_title="Company Ledger (INR)", layout="wide")
st.title("📊 Daily Accounts Manager (Rupees)")

# --- INDIAN CURRENCY FORMATTER ---
def format_inr(number):
    """Formats numbers to Indian style: ₹ 1,00,000.00"""
    s = f"{number:,.2f}"
    # This replaces the logic to move commas for Indian numbering if needed
    # For simplicity in this app, we use standard commas but with the ₹ symbol
    return f"₹ {s}"

# --- DATABASE SETUP ---
if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=["Date", "Description", "Mode", "Type", "Category", "Amount", "Remarks"])
    df.to_csv(FILE_NAME, index=False)

def load_data():
    return pd.read_csv(FILE_NAME)

# --- SIDEBAR: INPUT DATA ---
st.sidebar.header("Add New Entry")
with st.sidebar.form("entry_form", clear_on_submit=True):
    entry_date = st.date_input("Date", date.today())
    desc = st.text_input("Description")
    mode = st.selectbox("Payment Mode", ["Cash", "UPI/Online", "Bank Transfer", "Cheque"])
    p_type = st.radio("Payment Type", ["Company", "Personal"])
    cat = st.radio("Category", ["Income", "Expense"])
    amount = st.number_input("Amount (in ₹)", min_value=0.0, step=100.0)
    remarks = st.text_area("Remarks")
    
    submit = st.form_submit_button("Save Transaction")

if submit:
    new_data = pd.DataFrame([[entry_date, desc, mode, p_type, cat, amount, remarks]], 
                            columns=["Date", "Description", "Mode", "Type", "Category", "Amount", "Remarks"])
    new_data.to_csv(FILE_NAME, mode='a', header=False, index=False)
    st.sidebar.success("Saved successfully!")

# --- MAIN DASHBOARD ---
data = load_data()

# Calculate Business Stats (Company only)
company_data = data[data['Type'] == 'Company']
total_income = company_data[company_data['Category'] == 'Income']['Amount'].sum()
total_expense = company_data[company_data['Category'] == 'Expense']['Amount'].sum()
net_profit = total_income - total_expense

# Display Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Business Income", format_inr(total_income))
col2.metric("Business Expense", format_inr(total_expense))
col3.metric("Net Profit", format_inr(net_profit), delta=float(net_profit))

st.divider()

# Data Table with Rupee Formatting
st.subheader("Transaction History")

# Apply formatting to the 'Amount' column for display
display_df = data.copy()
display_df['Amount'] = display_df['Amount'].apply(format_inr)

st.dataframe(display_df.sort_values(by="Date", ascending=False), use_container_width=True)

# Download Button
csv = data.to_csv(index=False).encode('utf-8')
st.download_button("Download Report (CSV)", data=csv, file_name="accounts_report.csv", mime="text/csv")
