import streamlit as st
import pandas as pd
from gspread_helper import load_inventory_from_gsheet, update_inventory_to_gsheet

# Sheet config
sheet_id = "1V61WCd-bGiLTwrdQKr1WccSIEZ570Ft9WLPdlxdiVJA"
sheet_name = "inv_check"

def run_inventory_app():
    st.title("🧮 Inventory Management")

    # Load data
    inv = load_inventory_from_gsheet(sheet_id, sheet_name)

    # User selects Category, Size, Item
    category = st.selectbox("Select Category", sorted(inv["Category"].unique()))
    size = st.selectbox("Select Size", sorted(inv[inv["Category"] == category]["Size"].unique()))
    item = st.selectbox("Select Item", sorted(inv[(inv["Category"] == category) & (inv["Size"] == size)]["Item"].unique()))

    row_filter = (inv["Category"] == category) & (inv["Size"] == size) & (inv["Item"] == item)
    selected_row = inv[row_filter].copy()

    if selected_row.empty:
        st.warning("No item found. Please check your selection.")
        return

    # Inputs
    st.subheader("Add to Inventory")
    add_type = st.radio("Add in:", ["Box", "Packets/Nos"], horizontal=True)
    add_qty = st.number_input(f"Enter quantity to add ({add_type})", min_value=0, step=1)

    if st.button("➕ Add to Diesel Engine"):
        if add_qty > 0:
            packets_per_box = int(selected_row["Packets_per_Box"].values[0])
            add_packets = add_qty * packets_per_box if add_type == "Box" else add_qty
            inv.loc[row_filter, "Diesel_Engine"] += add_packets
            inv.loc[row_filter, "Total_Packets"] = inv.loc[row_filter, "Diesel_Engine"] + inv.loc[row_filter, "Rack"]
            update_inventory_to_gsheet(sheet_id, sheet_name, inv)
            st.success(f"Added {add_packets} packets to Diesel Engine.")

    st.subheader("Move Packets to Rack")
    move_qty = st.number_input("Enter packets to move to Rack", min_value=0, step=1)
    if st.button("🚚 Move to Rack"):
        available = int(inv.loc[row_filter, "Diesel_Engine"].values[0])
        if move_qty <= available:
            inv.loc[row_filter, "Diesel_Engine"] -= move_qty
            inv.loc[row_filter, "Rack"] += move_qty
            inv.loc[row_filter, "Total_Packets"] = inv.loc[row_filter, "Diesel_Engine"] + inv.loc[row_filter, "Rack"]
            update_inventory_to_gsheet(sheet_id, sheet_name, inv)
            st.success(f"Moved {move_qty} packets to Rack.")
        else:
            st.error(f"Not enough packets in Diesel Engine. Available: {available}")

    st.subheader("Subtract from Rack (moved to Shop)")
    sub_qty = st.number_input("Enter packets to subtract from Rack", min_value=0, step=1)
    if st.button("➖ Subtract from Rack"):
        available = int(inv.loc[row_filter, "Rack"].values[0])
        if sub_qty <= available:
            inv.loc[row_filter, "Rack"] -= sub_qty
            inv.loc[row_filter, "Total_Packets"] = inv.loc[row_filter, "Diesel_Engine"] + inv.loc[row_filter, "Rack"]
            update_inventory_to_gsheet(sheet_id, sheet_name, inv)
            st.success(f"Subtracted {sub_qty} packets from Rack.")
        else:
            st.error(f"Not enough packets in Rack. Available: {available}")

    st.subheader("📊 Inventory Status")
    if st.button("🔄 Show Current Inventory"):
        def highlight_low(val):
            try:
                return 'background-color: #ffcccc' if int(val) < 10 else ''
            except:
                return ''

        display_df = inv[["Category", "Size", "Item", "Diesel_Engine", "Rack", "Total_Packets"]]
        st.dataframe(display_df.style.applymap(highlight_low, subset=["Rack"]))
