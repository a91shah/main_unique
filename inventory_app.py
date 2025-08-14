import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets config
SHEET_ID = "1V61WCd-bGiLTwrdQKr1WccSIEZ570Ft9WLPdlxdiVJA"
WORKSHEET_NAME = "Sheet1"
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def connect_to_gsheet():
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)
    return sheet


def load_data():
    sheet = connect_to_gsheet()
    df = pd.DataFrame(sheet.get_all_records())
    df.columns = df.columns.str.strip().str.replace(" ", "_")
    return df

def save_data(df):
    sheet = connect_to_gsheet()
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

def run_inventory_app():
    if 'inventory' not in st.session_state:
        st.session_state.inventory = load_data()

    st.title("🔧 Inventory Management")

    inv = st.session_state.inventory
    category_options = inv['Category'].dropna().unique()
    size_options = inv['Size'].dropna().unique()

    st.header("1️⃣ Select Inventory Item")
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_category = st.selectbox("Category", category_options)
    with col2:
        selected_size = st.selectbox("Size", size_options)
    with col3:
        filtered_items = inv[
            (inv['Category'] == selected_category) & 
            (inv['Size'] == selected_size)
        ]['Item'].dropna().unique()
        selected_item = st.selectbox("Item", filtered_items)

    item_row = inv[
        (inv['Category'] == selected_category) & 
        (inv['Size'] == selected_size) & 
        (inv['Item'] == selected_item)
    ]

    if item_row.empty:
        st.error("Item not found in inventory.")
        return

    idx = item_row.index[0]
    packets_per_box = int(inv.at[idx, 'Packets_per_Box'])

    st.header("2️⃣ Perform Inventory Operation")
    operation = st.selectbox("Choose Operation", [
        "Add to Diesel Engine", 
        "Add to Rack",
        "Move to Rack", 
        "Subtract from Rack",
        "Move to Shop"
    ])

    qty_type = st.radio("Enter Quantity In", ["Boxes", "Packets"], horizontal=True)
    qty = st.number_input("Enter Quantity", min_value=1)
    packets = qty * packets_per_box if qty_type == "Boxes" else qty

    if st.button("✅ Submit Operation"):
        if operation == "Add to Diesel Engine":
            inv.at[idx, 'Diesel_Engine'] += packets
            st.success(f"✅ {packets} packets added to Diesel Engine.")
        elif operation == "Add to Rack":
            inv.at[idx, 'Rack'] += packets
            st.success(f"✅ {packets} packets added to Rack.")   
        elif operation == "Move to Rack":
            if inv.at[idx, 'Diesel_Engine'] >= packets:
                inv.at[idx, 'Diesel_Engine'] -= packets
                inv.at[idx, 'Rack'] += packets
                st.success(f"📦 {packets} packets moved from Diesel Engine to Rack.")
            else:
                st.error("❌ Not enough packets in Diesel Engine.")
        elif operation == "Subtract from Rack":
            if inv.at[idx, 'Rack'] >= packets:
                inv.at[idx, 'Rack'] -= packets
                st.success(f"🛒 {packets} packets subtracted from Rack (moved to Shop).")
            else:
                st.error("❌ Not enough packets in Rack.")
        elif operation == "Move to Shop":
            if inv.at[idx, 'Diesel_Engine'] >= packets:
                inv.at[idx, 'Diesel_Engine'] -= packets
                st.success(f"🛒 {packets} packets subtracted from Diesel_Engine (moved to Shop).")
            else:
                st.error("❌ Not enough packets in Diesel_Engine.")        

        inv.at[idx, 'Total_Packets'] = inv.at[idx, 'Diesel_Engine'] + inv.at[idx, 'Rack']
        save_data(inv)
        st.success("💾 Inventory updated and saved to Google Sheet.")

    st.header("3️⃣ Inventory Status")
    if st.button("📊 Show Current Inventory"):
        display_df = inv.copy()
        display_df["Total_Packets"] = display_df["Diesel_Engine"] + display_df["Rack"]
        display_df["Diesel_Engine_Box"] = display_df["Diesel_Engine"] / display_df["Packets_per_Box"]
        display_df["Status"] = display_df["Rack"].apply(lambda x: "LOW" if x < 10 else "OK")

        def highlight_low(val):
            return 'color: red; font-weight: bold' if val == "LOW" else ''

        st.dataframe(display_df.style.applymap(highlight_low, subset=["Status"]))
        st.download_button("📥 Download Inventory CSV",
                           data=display_df.to_csv(index=False),
                           file_name="current_inventory.csv",
                           mime="text/csv")
        # 🔴 New Button for Low Status Items
    if st.button("🔴 Show Low Status Items"):
        low_df = inv.copy()
        low_df["Total_Packets"] = low_df["Diesel_Engine"] + low_df["Rack"]
        low_df["Status"] = low_df["Rack"].apply(lambda x: "LOW" if x < 10 else "OK")
        low_items = low_df[low_df["Status"] == "LOW"][["Category", "Size", "Item", "Total_Packets"]]

        if not low_items.empty:
            st.subheader("📉 Items with LOW Stock")
            st.dataframe(low_items)
        else:
            st.info("✅ No items are currently in LOW status.")





