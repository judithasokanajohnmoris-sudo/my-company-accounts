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
        df = pd.DataFrame(columns=["Date", "Description", "Mode", "Type", "Category", "Amount", "Remarks"])
        df.to_csv(FILE_NAME, index=False)
        return df
    
    df = pd.read_csv(FILE_NAME)
    # Ensure Date is in datetime format for proper sorting
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce').dt.date.astype(str)
    df["Amount"] = pd.to_numeric(df["Amount"], errors='coerce').fillna(0)
    df["Description"] = df["Description"].fillna("").astype(str)
    df["Remarks"] = df["Remarks"].fillna("").astype(str)
    return df

def save_data(df):
    # Sort by date before saving to keep things organized like Excel
    df = df.sort_values(by="Date", ascending=False)
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

# --- CALCULATIONS ---
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

# --- MANAGE TRANSACTIONS ---
st.subheader("📝 Manage Transactions")
st.info("💡 To 'Insert' a row: Add a new row at the bottom using the (+) icon, set the Date, and click Save. The app will automatically move it to the correct position.")

# Filter/Search
search_query = st.text_input("🔍 Search entries...", "").lower()
if search_query:
    display_df = data[data['Description'].str.lower().str.contains(search_query) | data['Remarks'].str.lower().str.contains(search_query)]
else:
    display_df = data

# Data Editor
edited_df = st.data_editor(
    display_df,
    num_rows="dynamic", # This allows you to add/delete rows
    use_container_width=True,
    column_config={
        "Mode": st.column_config.SelectboxColumn("Mode", options=["Cash", "UPI/Online", "Bank Transfer", "Cheque"]),
        "Type": st.column_config.SelectboxColumn("Type", options=["Company", "Personal"]),
        "Category": st.column_config.SelectboxColumn("Category", options=["Income", "Expense"]),
        "Date": st.column_config.DateColumn("Date")
    }
)

if st.button("💾 Save & Re-organize"):
    save_data(edited_df)
    st.success("Re-organized by Date!")
    st.rerun()

st.divider()

# --- DOWNLOADS ---
st.subheader("📥 Export Reports")
c1, c2, c3 = st.columns(3)
c1.download_button("🟢 Master CSV", data.to_csv(index=False).encode('utf-8'), "Master_Data.csv")
c2.download_button("Company CSV", company_only.to_csv(index=False).encode('utf-8'), "Company_Report.csv")
c3.download_button("Personal CSV", data[data['Type']=='Personal'].to_csv(index=False).encode('utf-8'), "Personal_Report.csv")
