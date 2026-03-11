import streamlit as st
import pandas as pd
from datetime import date
import os
import io

# --- SETTINGS ---
FILE_NAME = "my_accounts.csv"

st.set_page_config(page_title="Vortex Care Accounts Pro", layout="wide")
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

# --- EDITING SECTION ---
st.subheader("📝 Edit & Manage Transactions")
edited_df = st.data_editor(data, num_rows="dynamic", use_container_width=True, key="main_editor")

if st.button("💾 Save Changes to Database"):
    save_data(edited_df)
    st.success("Changes saved successfully!")
    st.rerun()

st.divider()

# --- REPORTS SECTION ---
st.subheader("📥 Download Reports")
col1, col2, col3 = st.columns(3)

# Function to convert DF to Excel Bytes
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

with col1:
    st.write("**Full Master Backup**")
    st.download_button(
        label="🟢 Download All Data (Excel)",
        data=to_excel(data),
        file_name=f"Master_Accounts_{date.today()}.xlsx",
        mime="application/vnd.ms-excel"
    )

with col2:
    st.write("**Company Only**")
    comp_csv = data[data['Type'] == 'Company'].to_csv(index=False).encode('utf-8')
    st.download_button("Download Company CSV", data=comp_csv, file_name="company_report.csv", mime="text/csv")

with col3:
    st.write("**Personal Only**")
    pers_csv = data[data['Type'] == 'Personal'].to_csv(index=False).encode('utf-8')
    st.download_button("Download Personal CSV", data=pers_csv, file_name="personal_report.csv", mime="text/csv")
