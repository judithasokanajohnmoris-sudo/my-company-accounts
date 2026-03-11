import streamlit as st
import pandas as pd
from datetime import date
import os

# --- SETTINGS ---
FILE_NAME = "my_accounts.csv"

st.set_page_config(page_title="Vortex Care Accounts", layout="wide")
st.title("📊 Daily Accounts Manager")

# --- DATABASE SETUP ---
if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=["Date", "Description", "Mode", "Type", "Category", "Amount", "Remarks"])
    df.to_csv(FILE_NAME, index=False)

def load_data():
    df = pd.read_csv(FILE_NAME)
    df["Amount"] = pd.to_numeric(df["Amount"], errors='coerce').fillna(0)
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
filtered_df = data[
    data['Description'].str.lower().str.contains(search_query, na=False) | 
    data['Remarks'].str.lower().str.contains(search_query, na=False)
]

# Data Editor (using filtered data)
edited_df = st.data_editor(filtered_df, num_rows="dynamic", use_container_width=True, key="main_editor")

if st.button("💾 Save Changes"):
    # If a search was active, we merge the edited filtered data back into the main data
    data.update(edited_df)
    save_data(edited_df if search_query == "" else data)
    st.success("Database Updated!")
    st.rerun()

st.divider()

# --- REPORTS SECTION (ALL CSV) ---
st.subheader("📥 Download CSV Reports")
col1, col2, col3 = st.columns(3)

with col1:
    master_csv = data.to_csv(index=False).encode('utf-8')
    st.download_button("🟢 Download All Data (CSV)", data=master_csv, file_name="Master_Accounts.csv", mime="text/csv")

with col2:
    comp_csv = data[data['Type'] == 'Company'].to_csv(index=False).encode('utf-8')
    st.download_button("Download Company CSV", data=comp_csv, file_name="company_report.csv", mime="text/csv")

with col3:
    pers_csv = data[data['Type'] == 'Personal'].to_csv(index=False).encode('utf-8')
    st.download_button("Download Personal CSV", data=pers_csv, file_name="personal_report.csv", mime="text/csv")
