import streamlit as st
import pandas as pd
from datetime import date
import os

# --- SETTINGS ---
FILE_NAME = "my_accounts.csv"

st.set_page_config(page_title="Company Ledger 2026", layout="wide")
st.title("📊 Daily Accounts Manager")

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
    mode = st.selectbox("Payment Mode", ["Cash", "UPI/Online", "Bank Transfer", "Card"])
    p_type = st.radio("Payment Type", ["Company", "Personal"])
    cat = st.radio("Category", ["Income", "Expense"])
    amount = st.number_input("Amount", min_value=0.0, step=1.0)
    remarks = st.text_area("Remarks")
    
    submit = st.form_submit_button("Save Transaction")

if submit:
    new_data = pd.DataFrame([[entry_date, desc, mode, p_type, cat, amount, remarks]], 
                            columns=["Date", "Description", "Mode", "Type", "Category", "Amount", "Remarks"])
    new_data.to_csv(FILE_NAME, mode='a', header=False, index=False)
    st.sidebar.success("Saved successfully!")

# --- MAIN DASHBOARD ---
data = load_data()

# Quick Stats
company_data = data[data['Type'] == 'Company']
total_income = company_data[company_data['Category'] == 'Income']['Amount'].sum()
total_expense = company_data[company_data['Category'] == 'Expense']['Amount'].sum()
net_profit = total_income - total_expense

col1, col2, col3 = st.columns(3)
col1.metric("Total Company Income", f"${total_income:,.2f}")
col2.metric("Total Company Expense", f"${total_expense:,.2f}")
col3.metric("Net Business Profit", f"${net_profit:,.2f}", delta=net_profit)

st.divider()

# Data Table
st.subheader("Transaction History")
st.dataframe(data.sort_values(by="Date", ascending=False), use_container_width=True)

# Download Button
csv = data.to_csv(index=False).encode('utf-8')
st.download_button("Download Excel/CSV Report", data=csv, file_name="accounts_report.csv", mime="text/csv")
