import streamlit as st
import pandas as pd

# Set page layout
st.set_page_config(page_title="Vehicle Maintenance Dashboard", layout="wide")
st.title("🚗 Vehicle Maintenance Dashboard")

# Function to load data from Google Sheets
@st.cache_data(ttl=60) # Caches data for 60 seconds so it updates quickly
def load_data(sheet_url):
    # Read the data from the Google Sheets CSV link
    # Skipping the first 2 rows to match the format of your uploaded Excel file
    df = pd.read_csv(sheet_url, skiprows=2)
    
    # Clean up empty rows
    df = df.dropna(subset=['Plate No.']) 
    return df

# --- YOUR GOOGLE SHEETS LINK GOES HERE ---
# Replace this placeholder with your actual published CSV link from Google Sheets
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQmIFmk-UKpfLELfVtJn42quNxCQIkUS3YIB9NB1tTbf_6CroRzUibQeJ1twQOA1Q/pub?gid=575821024&single=true&output=csv" 

try:
    # If you want to test locally with your Excel file first, uncomment the line below:
    # df = pd.read_excel("Technical Pioneers for Car Maintenance2025 -2026.xlsx", sheet_name='Sheet2', skiprows=2)
    
    # Loads live data from Google Sheets
    df = load_data(GOOGLE_SHEET_CSV_URL)
except Exception as e:
    st.error(f"Error loading data. Please check your Google Sheets link. Details: {e}")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("🔍 Search & Filter")

# Vehicle Search (Plate No.)
vehicle_list = df['Plate No.'].unique().tolist()
selected_vehicle = st.sidebar.selectbox("Search Vehicle No. (Plate No.)", ["All"] + vehicle_list)

# Department Search
dept_list = df['Department'].dropna().unique().tolist()
selected_dept = st.sidebar.selectbox("Search Department", ["All"] + dept_list)

# Payment Status Filter
status_list = df['Payment status'].dropna().unique().tolist()
selected_status = st.sidebar.selectbox("Payment Status", ["All"] + status_list)

# --- Apply Filters ---
filtered_df = df.copy()

if selected_vehicle != "All":
    filtered_df = filtered_df[filtered_df['Plate No.'] == selected_vehicle]

if selected_dept != "All":
    filtered_df = filtered_df[filtered_df['Department'] == selected_dept]

if selected_status != "All":
    filtered_df = filtered_df[filtered_df['Payment status'] == selected_status]

# --- Dashboard Metrics ---
st.markdown("### 📊 Cost Summary")
col1, col2, col3, col4 = st.columns(4)

total_spend = filtered_df['Total Cost with VAT'].sum()
paid_amount = filtered_df[filtered_df['Payment status'] == 'PAID']['Total Cost with VAT'].sum()
unpaid_amount = filtered_df[filtered_df['Payment status'] == 'UNPAID']['Total Cost with VAT'].sum()
total_vehicles = filtered_df['Plate No.'].nunique()

col1.metric("Total Spend (w/ VAT)", f"{total_spend:,.2f}")
col2.metric("Total PAID", f"{paid_amount:,.2f}")
col3.metric("Total UNPAID", f"{unpaid_amount:,.2f}")
col4.metric("Vehicles Maintained", total_vehicles)

# --- Detailed Tables ---
st.markdown("---")
st.markdown("### 🚘 Vehicle List & Maintenance Records")
st.dataframe(
    filtered_df[['Date', 'Invoice No.', 'Plate No.', 'Car Model', 'Description', 'Department', 'Total Cost with VAT', 'Payment status']], 
    use_container_width=True,
    hide_index=True
)