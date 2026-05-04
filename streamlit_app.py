import streamlit as st
import pandas as pd
from datetime import date
import os
import plotly.express as px  # Recommended for quick charts

# --- SETTINGS ---
FILE_NAME = "my_accounts.csv"

st.set_page_config(page_title="Vortex Care Accounts", layout="wide", page_icon="📊")

# --- DATABASE SETUP ---
def load_data():
    if not os.path.exists(FILE_NAME):
        df = pd.DataFrame(columns=["Date", "Description", "Mode", "Type", "Category", "Amount", "Remarks"])
        df.to_csv(FILE_NAME, index=False)
        return df
    
    df = pd.read_csv(FILE_NAME)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    df = df.sort_values(by="Date", ascending=False) # Newest first for better visibility
    return df

def save_data(df):
    df_to_save = df.copy()
    df_to_save["Date"] = df_to_save["Date"].astype(str)
    df_to_save.to_csv(FILE_NAME, index=False)

# Initial Load
if 'df' not in st.session_state:
    st.session_state.df = load_data()

# --- SIDEBAR: NEW ENTRY ---
with st.sidebar:
    st.header("➕ Add New Entry")
    with st.form("entry_form", clear_on_submit=True):
        entry_date = st.date_input("Date", date.today())
        desc = st.text_input("Description")
        mode = st.selectbox("Mode", ["Cash", "UPI/Online", "Bank Transfer", "Cheque"])
        p_type = st.radio("Type", ["Company", "Personal"], horizontal=True)
        cat = st.radio("Category", ["Income", "Expense"], horizontal=True)
        amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
        remarks = st.text_area("Remarks")
        submit = st.form_submit_button("Save Transaction", use_container_width=True)

    if submit:
        if desc:
            new_row = pd.DataFrame([[entry_date, desc, mode, p_type, cat, amount, remarks]], 
                                    columns=st.session_state.df.columns)
            st.session_state.df = pd.concat([new_row, st.session_state.df], ignore_index=True)
            save_data(st.session_state.df)
            st.success("Transaction Logged!")
            st.rerun()
        else:
            st.error("Please enter a description.")

# --- MAIN DASHBOARD ---
st.title("📊 Vortex Care: Daily Accounts")

# Calculations (Company Only)
company_df = st.session_state.df[st.session_state.df['Type'] == 'Company']
total_inc = company_df[company_df['Category'] == 'Income']['Amount'].sum()
total_exp = company_df[company_df['Category'] == 'Expense']['Amount'].sum()
balance = total_inc - total_exp

# Summary Cards
m1, m2, m3 = st.columns(3)
m1.metric("Total Income", f"₹{total_inc:,.2f}")
m2.metric("Total Expenses", f"₹{total_exp:,.2f}")
m3.metric("Net Balance", f"₹{balance:,.2f}", delta=float(balance))

st.divider()

# --- SEARCH & EDIT ---
col_head, col_search = st.columns([2, 1])
with col_head:
    st.subheader("📝 Transaction Ledger")
with col_search:
    search = st.text_input("", placeholder="🔍 Search description...")

display_df = st.session_state.df
if search:
    display_df = display_df[display_df['Description'].str.contains(search, case=False, na=False)]

edited_df = st.data_editor(
    display_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
        "Amount": st.column_config.NumberColumn("Amount (₹)", format="₹%.2f"),
        "Category": st.column_config.SelectboxColumn("Category", options=["Income", "Expense"]),
        "Type": st.column_config.SelectboxColumn("Type", options=["Company", "Personal"])
    },
    key="ledger_editor"
)

if st.button("💾 Commit Changes to Disk"):
    save_data(edited_df)
    st.session_state.df = edited_df
    st.toast("Database Updated!", icon="✅")

# --- EXPORTS ---
with st.expander("📥 Export Reports"):
    c1, c2, c3 = st.columns(3)
    csv_all = st.session_state.df.to_csv(index=False).encode('utf-8')
    c1.download_button("Download All Data", csv_all, "Master_Ledger.csv", "text/csv", use_container_width=True)
    # Add logic for filtered CSVs here if needed
