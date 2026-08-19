import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="Vehicle Maintenance Dashboard", layout="wide")
st.title("🚗 Vehicle Maintenance Dashboard")

# --- Data Loading & Cleaning ---
@st.cache_data(ttl=60) # Caches data for 60 seconds for quick refreshes
def load_data(sheet_url):
    # Read the data from the Google Sheets CSV link
    # NOTE: skiprows=2 has been removed because headers are now on row 1
    df = pd.read_csv(sheet_url)
    
    # Clean up empty rows where there is no Plate No.
    if 'Plate No.' in df.columns:
        df = df.dropna(subset=['Plate No.']) 
    else:
        st.error("Column 'Plate No.' not found. Please verify the Google Sheets link is correct and headers are on the first row.")
        st.stop()
    
    # --- Data Type Fix ---
    # Convert 'Total Cost with VAT' from text to a number for calculations
    if 'Total Cost with VAT' in df.columns:
        df['Total Cost with VAT'] = df['Total Cost with VAT'].astype(str).str.replace(',', '')
        df['Total Cost with VAT'] = pd.to_numeric(df['Total Cost with VAT'], errors='coerce').fillna(0)
    
    return df

# --- GOOGLE SHEETS LINK ---
# Replace this placeholder with your actual published CSV link from Google Sheets
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQmIFmk-UKpfLELfVtJn42quNxCQIkUS3YIB9NB1tTbf_6CroRzUibQeJ1twQOA1Q/pub?gid=575821024&single=true&output=csv" 

try:
    df = load_data(GOOGLE_SHEET_CSV_URL)
except Exception as e:
    st.error(f"Error loading data. Details: {e}")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("🔍 Search & Filter")

# Vehicle Search (Plate No.)
vehicle_list = df['Plate No.'].unique().tolist()
selected_vehicle = st.sidebar.selectbox("Search Vehicle No. (Plate No.)", ["All"] + vehicle_list)

# Department Search
if 'Department' in df.columns:
    dept_list = df['Department'].dropna().unique().tolist()
    selected_dept = st.sidebar.selectbox("Search Department", ["All"] + dept_list)
else:
    selected_dept = "All"

# Payment Status Filter
if 'Payment status' in df.columns:
    status_list = df['Payment status'].dropna().unique().tolist()
    selected_status = st.sidebar.selectbox("Payment Status", ["All"] + status_list)
else:
    selected_status = "All"

# --- Apply Filters ---
filtered_df = df.copy()

if selected_vehicle != "All":
    filtered_df = filtered_df[filtered_df['Plate No.'] == selected_vehicle]

if selected_dept != "All" and 'Department' in df.columns:
    filtered_df = filtered_df[filtered_df['Department'] == selected_dept]

if selected_status != "All" and 'Payment status' in df.columns:
    filtered_df = filtered_df[filtered_df['Payment status'] == selected_status]

# --- Dashboard Metrics ---
st.markdown("### 📊 Cost Summary")
col1, col2, col3, col4 = st.columns(4)

if 'Total Cost with VAT' in filtered_df.columns:
    total_spend = filtered_df['Total Cost with VAT'].sum()
    paid_amount = filtered_df[filtered_df['Payment status'] == 'PAID']['Total Cost with VAT'].sum() if 'Payment status' in filtered_df.columns else 0
    unpaid_amount = filtered_df[filtered_df['Payment status'] == 'UNPAID']['Total Cost with VAT'].sum() if 'Payment status' in filtered_df.columns else 0
else:
    total_spend, paid_amount, unpaid_amount = 0, 0, 0

total_vehicles = filtered_df['Plate No.'].nunique()

# Formatting numbers with commas and 2 decimal places
col1.metric("Total Spend (w/ VAT)", f"{total_spend:,.2f}")
col2.metric("Total PAID", f"{paid_amount:,.2f}")
col3.metric("Total UNPAID", f"{unpaid_amount:,.2f}")
col4.metric("Vehicles Maintained", total_vehicles)

# --- Detailed Tables ---
st.markdown("---")
st.markdown("### 🚘 Vehicle List & Maintenance Records")

# Columns to display if they exist
display_cols = [col for col in ['Date', 'Invoice No.', 'Plate No.', 'Car Model', 'Description', 'Department', 'Total Cost with VAT', 'Payment status'] if col in filtered_df.columns]

st.dataframe(
    filtered_df[display_cols], 
    use_container_width=True,
    hide_index=True
)
