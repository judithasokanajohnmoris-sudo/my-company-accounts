import streamlit as st
import pandas as pd
from datetime import date
import os

# --- SETTINGS ---
FILE_NAME = "my_accounts.csv"

st.set_page_config(page_title="Vortex Care Accounts", layout="wide")
st.title("📊 Vortex Care: Professional Ledger")

# --- DATABASE SETUP ---
def load_data():
    if not os.path.exists(FILE_NAME):
        # Added 'Method' column to the structure
        df = pd.DataFrame(columns=["Date", "Description", "Method", "Mode", "Type", "Category", "Amount", "Remarks"])
        df.to_csv(FILE_NAME, index=False)
        return df
    
    df = pd.read_csv(FILE_NAME)
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce').dt.date
    df["Date"] = df["Date"].fillna(date.today())
    df = df.sort_values(by="Date", ascending=True)
    
    # Ensure all columns exist and are clean
    cols = ["Date", "Description", "Method", "Mode", "Type", "Category", "Amount", "Remarks"]
    for col in cols:
        if col not in df.columns:
            df[col] = ""
            
    df["Amount"] = pd.to_numeric(df["Amount"], errors='coerce').fillna(0)
    return df

def save_data(df):
    df = df.sort_values(by="Date", ascending=True)
    df_to_save = df.copy()
    df_to_save["Date"] = df_to_save["Date"].astype(str)
    df_to_save.to_csv(FILE_NAME, index=False)

# --- SIDEBAR: ENTRY ---
st.sidebar.header("➕ Add New Entry")
with st.sidebar.form("entry_form", clear_on_submit=True):
    entry_date = st.date_input("Date", date.today())
    desc = st.text_input("Description")
    
    # New Specific Heads for daily tracking
    method = st.selectbox("Payment Method", ["Cash", "UPI", "Bank Transfer", "Card", "Cheque"])
    
    # Logic to auto-select Account Head based on Method
    account_head = "Cash A/c" if method == "Cash" else "Bank A/c"
    
    p_type = st.radio("Type", ["Company", "Personal"])
    cat = st.radio("Category", ["Income", "Expense"])
    amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
    remarks = st.text_area("Remarks")
    submit = st.form_submit_button("Save Transaction")

if submit:
    # Save both the specific Method and the Account Head (Mode)
    new_row = pd.DataFrame([[entry_date, desc, method, account_head, p_type, cat, amount, remarks]], 
                            columns=["Date", "Description", "Method", "Mode", "Type", "Category", "Amount", "Remarks"])
    current_df = load_data()
    updated_df = pd.concat([current_df, new_row], ignore_index=True)
    save_data(updated_df)
    st.sidebar.success(f"Saved to {account_head}!")
    st.rerun()

# --- CALCULATION LOGIC ---
data = load_data()

def get_balances(df):
    cash_in = df[(df['Mode'] == 'Cash A/c') & (df['Category'] == 'Income')]['Amount'].sum()
    cash_out = df[(df['Mode'] == 'Cash A/c') & (df['Category'] == 'Expense')]['Amount'].sum()
    bank_in = df[(df['Mode'] == 'Bank A/c') & (df['Category'] == 'Income')]['Amount'].sum()
    bank_out = df[(df['Mode'] == 'Bank A/c') & (df['Category'] == 'Expense')]['Amount'].sum()
    return (cash_in - cash_out), (bank_in - bank_out)

today = date.today()
past_data = data[data['Date'] < today]
op_cash, op_bank = get_balances(past_data)
cl_cash, cl_bank = get_balances(data)

# --- DISPLAY METRICS ---
st.subheader("🏦 Opening Balances (Today)")
o1, o2, o3 = st.columns(3)
o1.metric("Opening Cash", f"₹{op_cash:,.2f}")
o2.metric("Opening Bank", f"₹{op_bank:,.2f}")
o3.metric("Total Opening", f"₹{op_cash + op_bank:,.2f}")

st.subheader("🚩 Closing Balances (Live)")
c1, c2, c3 = st.columns(3)
c1.metric("Closing Cash", f"₹{cl_cash:,.2f}", delta=float(cl_cash - op_cash))
c2.metric("Closing Bank", f"₹{cl_bank:,.2f}", delta=float(cl_bank - op_bank))
c3.metric("Total Net Worth", f"₹{cl_cash + cl_bank:,.2f}")

st.divider()

# --- MANAGE TRANSACTIONS ---
st.subheader("📝 Daily Ledger")
search_query = st.text_input("🔍 Search entries...", "").lower()
display_df = data if not search_query else data[data['Description'].str.lower().str.contains(search_query)]

edited_df = st.data_editor(
    display_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
        "Method": st.column_config.SelectboxColumn("Payment Method", options=["Cash", "UPI", "Bank Transfer", "Card", "Cheque"]),
        "Mode": st.column_config.SelectboxColumn("Account Head", options=["Cash A/c", "Bank A/c"]),
        "Type": st.column_config.SelectboxColumn("Type", options=["Company", "Personal"]),
        "Category": st.column_config.SelectboxColumn("Category", options=["Income", "Expense"]),
    },
    key="main_editor"
)

if st.button("💾 Save Changes"):
    # Re-sync Mode based on Method before saving
    edited_df["Mode"] = edited_df["Method"].apply(lambda x: "Cash A/c" if x == "Cash" else "Bank A/c")
    save_data(edited_df)
    st.success("Ledger Updated!")
    st.rerun()

# --- DOWNLOADS ---
st.divider()
st.download_button("🟢 Download Master CSV", data.to_csv(index=False).encode('utf-8'), "Vortex_Accounts_Master.csv")
