# --- SIDEBAR: UPLOAD EXCEL ---
st.sidebar.header("📂 Upload Previous Data")

uploaded_file = st.sidebar.file_uploader("Upload Excel or CSV", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        # Read file
        if uploaded_file.name.endswith('.xlsx'):
            new_data = pd.read_excel(uploaded_file)
        else:
            new_data = pd.read_csv(uploaded_file)

        st.sidebar.write("Preview of uploaded data:")
        st.sidebar.dataframe(new_data.head())

        # --- REQUIRED COLUMNS ---
        required_columns = ["Date", "Description", "Mode", "Type", "Category", "Amount", "Remarks"]

        # Check missing columns
        missing_cols = [col for col in required_columns if col not in new_data.columns]

        if missing_cols:
            st.sidebar.error(f"Missing columns: {missing_cols}")
        else:
            # Clean Data
            new_data["Date"] = pd.to_datetime(new_data["Date"], errors='coerce').dt.date
            new_data["Date"] = new_data["Date"].fillna(date.today())

            new_data["Amount"] = pd.to_numeric(new_data["Amount"], errors='coerce').fillna(0)

            for col in ["Description", "Remarks", "Mode", "Type", "Category"]:
                new_data[col] = new_data[col].fillna("").astype(str)

            if st.sidebar.button("➕ Import Data"):
                existing_data = load_data()
                combined_data = pd.concat([existing_data, new_data], ignore_index=True)

                save_data(combined_data)

                st.sidebar.success("Data Imported Successfully!")
                st.rerun()

    except Exception as e:
        st.sidebar.error(f"Error: {e}")
