import streamlit as st
import pandas as pd
from datetime import date
import os

# --- SETTINGS ---
FILE_NAME = "my_accounts.csv"

st.set_page_config(page_title="Company Ledger Pro", layout="wide")
st.title("📊 Daily Accounts Manager")

# --- DATABASE SETUP ---
if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=["Date", "Description", "Mode", "Type", "Category", "Amount", "Remarks"])
    df.to_csv(FILE_NAME, index=False)

def load_data():
    return pd.read_csv(FILE_NAME)

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

# --- MAIN DASHBOARD ---
data = load_data()

# 1. EDITING SECTION
st.subheader("📝 Edit & Manage Transactions")
st.info("💡 Tip: Double-click any cell to edit. Use the 'Save Changes' button below the table to update your records.")

# Use data_editor to allow live editing
edited_df = st.data_editor(data, num_rows="dynamic", use_container_width=True, key="editor")

if st.button("💾 Save All Changes"):
    save_data(edited_df)
    st.success("All changes have been saved to the database!")
    st.rerun()

st.divider()

# 2. SEPARATE DOWNLOADS
st.subheader("📥 Download Reports")
col_comp, col_pers = st.columns(2)

# Filter data
company_df = data[data['Type'] == 'Company']
personal_df = data[data['Type'] == 'Personal']

with col_comp:
    st.write(f"**Company Records:** {len(company_df)} entries")
    st.download_button(
        label="Download Company Transactions (CSV)",
        data=company_df.to_csv(index=False).encode('utf-8'),
        file_name=f"company_accounts_{date.today()}.csv",
        mime="text/csv"
    )

with col_pers:
    st.write(f"**Personal Records:** {len(personal_df)} entries")
    st.download_button(
        label="Download Personal Transactions (CSV)",
        data=personal_df.to_csv(index=False).encode('utf-8'),
        file_name=f"personal_accounts_{date.today()}.csv",
        mime="text/csv"
    )
