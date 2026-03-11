import streamlit as st
import pandas as pd
from datetime import date
import os

# --- SETTINGS ---
FILE_NAME = "my_accounts.csv"

st.set_page_config(page_title="Vortex Care Accounts", layout="wide")
st.title("📊 Vortex Care: Daily Accounts Manager")

# --- DATABASE SETUP ---
def load_data():
    if not os.path.exists(FILE_NAME):
        # Create empty file with correct columns if not exists
        df = pd.DataFrame(columns=["Date", "Description", "Mode", "Type", "Category", "Amount", "Remarks"])
        df.to_csv(FILE_NAME, index=False)
        return df
    
    df = pd.read_csv(FILE_NAME)
    # Ensure columns exist
    cols = ["Date", "Description", "Mode", "Type", "Category", "Amount", "Remarks"]
    for col in cols:
        if col not in df.columns:
            df[col] = ""
            
    # CRITICAL FIX: Convert everything to string first, then handle numbers
    df["Amount"] = pd.to_numeric(df["Amount"], errors='coerce').fillna(0)
    df["Description"] = df["Description"].fillna("").astype(str)
    df["Remarks"] = df["Remarks"].fillna("").astype(str)
    df["Date"] = df["Date"].astype(str)
    return df

def save_data(df):
    df.to_csv(FILE_NAME, index=False)

# --- SIDEBAR: NEW ENTRY ---
st.sidebar.header("➕ Add New Entry")
with st.sidebar.form("entry_form", clear_on_submit=True):
    entry_date = st.date_input("Date", date.today())
    desc = st.text_input("Description")
    mode = st.selectbox("Payment Mode", ["Cash", "UPI/Online", "Bank Transfer", "Cheque"])
    p_type = st.radio("Payment Type", ["Company", "Personal"])
    cat = st.radio("Category", ["Income", "Expense"])
    amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
    remarks = st.text_area("Remarks")
    submit = st.form_submit_button("Save Transaction")

if submit:
    new_row = pd.DataFrame([[str(entry_date), desc, mode, p_type, cat, amount, remarks]], 
                            columns=["Date", "Description", "Mode", "Type", "Category", "Amount", "Remarks"])
    current_df = load_data()
    updated_df = pd.concat([current_df, new_row], ignore_index=True)
    save_data(updated_df)
    st.sidebar.success("Saved!")
    st.rerun()

# --- CALCULATIONS & METRICS ---
data = load_data()
company_only = data[data['Type'] == 'Company']
total_inc = company_only[company_only['Category'] == 'Income']['Amount'].sum()
total_exp = company_only[company_only['Category'] == 'Expense']['Amount'].sum()
net_profit = total_inc - total_exp

st.subheader("Business Summary (Company Only)")
m1, m2, m3 = st.columns(3)
m1.metric("Total Income", f"₹{total_inc:,.2f}")
m2.metric("Total Expense", f"₹{total_exp:,.2f}")
m3.metric("Net Profit", f"₹{net_profit:,.2f}", delta=float(net_profit))

st.divider()

# --- SEARCH & EDIT SECTION ---
st.subheader("📝 Manage Transactions")

# Search bar
search_query = st.text_input("🔍 Search by Description or Remarks", "").lower()

# Filter logic with explicit string conversion for search
if search_query:
    filtered_df = data[
        data['Description'].str.lower().str.contains(search_query, na=False) | 
        data['Remarks'].str.lower().str.contains(search_query, na=False)
    ]
else:
    filtered_df = data

# Data Editor
edited_df = st.data_editor(filtered_df, num_rows="dynamic", use_container_width=True, key="main_editor")

if st.button("💾 Save All Changes"):
    if search_query == "":
        save_data(edited_df)
    else:
        # If filtered, merge the edited rows back into the original data
        data.update(edited_df)
        save_data(data)
    st.success("Database Updated!")
    st.rerun()

st.divider()

# --- DOWNLOADS ---
st.subheader("📥 Download CSV Reports")
col1, col2, col3 = st.columns(3)

with col1:
    st.download_button("🟢 Master Data (All)", data.to_csv(index=False).encode('utf-8'), "Master_Accounts.csv", "text/csv")
with col2:
    st.download_button("Company Report", data[data['Type'] == 'Company'].to_csv(index=False).encode('utf-8'), "Company_Report.csv", "text/csv")
with col3:
    st.download_button("Personal Report", data[data['Type'] == 'Personal'].to_csv(index=False).encode('utf-8'), "Personal_Report.csv", "text/csv")
