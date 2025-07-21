
import streamlit as st
import pandas as pd
from gspread_helper import load_inventory_from_gsheet, update_inventory_to_gsheet

def run_inventory_app():
    st.title("🧮 Inventory Management")

    # Sheet details
    sheet_id = "1V61WCd-bGiLTwrdQKr1WccSIEZ570Ft9WLPdlxdiVJA"
    sheet_name = "sheet1"

    # Load inventory
    inv = load_inventory_from_gsheet(sheet_id, sheet_name)

    if inv.empty:
        st.warning("No data found in the sheet.")
        return

    # User selections
    category = st.selectbox("Select Category", sorted(inv["Category"].dropna().unique()))
    filtered_inv = inv[inv["Category"] == category]

    if filtered_inv.empty:
        st.warning("No sizes found for selected category.")
        return

    size = st.selectbox("Select Size", sorted(filtered_inv["Size"].dropna().unique()))
    filtered_inv = filtered_inv[filtered_inv["Size"] == size]

    if filtered_inv.empty:
        st.warning("No items found for selected size.")
        return

    item = st.selectbox("Select Item", sorted(filtered_inv["Item"].dropna().unique()))
    row_index = inv[
        (inv["Category"] == category) &
        (inv["Size"] == size) &
        (inv["Item"] == item)
    ].index[0]

    # Show current status
    st.subheader("📦 Current Stock")
    st.write(inv.loc[row_index, ["Diesel_Engine", "Rack", "Total_Packets"]])

    st.markdown("---")

    # Add to Diesel Engine
    st.subheader("➕ Add Inventory to Diesel Engine")
    add_box = st.number_input("Enter number of Boxes to add", min_value=0, step=1, key="add_box")
    add_packets = st.number_input("Or enter number of Packets/Nos to add", min_value=0, step=1, key="add_packets")
    if st.button("Add to Diesel Engine"):
    update_inventory_to_gsheet(inv)
        packets_per_box = inv.loc[row_index, "Packets_per_Box"]
        added_packets = add_packets + (add_box * packets_per_box)
        inv.at[row_index, "Diesel_Engine"] += added_packets
        inv.at[row_index, "Total_Packets"] = inv.at[row_index, "Diesel_Engine"] + inv.at[row_index, "Rack"]
        update_inventory_to_gsheet(inv, sheet_id, sheet_name)
        st.success("✅ Added {} packets to Diesel Engine.".format(added_packets))

    # Move to Rack
    st.subheader("➡️ Move Inventory to Rack")
    move_packets = st.number_input("Enter number of packets to move", min_value=0, step=1, key="move_to_rack")
    if st.button("Move to Rack"):
    update_inventory_to_gsheet(inv)
        if move_packets > inv.at[row_index, "Diesel_Engine"]:
            st.error("❌ Not enough packets in Diesel Engine.")
        else:
            inv.at[row_index, "Diesel_Engine"] -= move_packets
            inv.at[row_index, "Rack"] += move_packets
            inv.at[row_index, "Total_Packets"] = inv.at[row_index, "Diesel_Engine"] + inv.at[row_index, "Rack"]
            update_inventory_to_gsheet(inv, sheet_id, sheet_name)
            st.success("✅ Moved {} packets to Rack.".format(move_packets))

    # Subtract from Rack
    st.subheader("➖ Subtract Inventory from Rack (Shop Dispatch)")
    subtract_packets = st.number_input("Enter number of packets to subtract", min_value=0, step=1, key="subtract_rack")
    if st.button("Subtract from Rack"):
    update_inventory_to_gsheet(inv)
        if subtract_packets > inv.at[row_index, "Rack"]:
            st.error("❌ Not enough packets in Rack.")
        else:
            inv.at[row_index, "Rack"] -= subtract_packets
            inv.at[row_index, "Total_Packets"] = inv.at[row_index, "Diesel_Engine"] + inv.at[row_index, "Rack"]
            update_inventory_to_gsheet(inv, sheet_id, sheet_name)
            st.success("✅ Subtracted {} packets from Rack.".format(subtract_packets))

    st.markdown("---")
    if st.button("📊 Show Current Inventory Status"):
        st.dataframe(inv)

if __name__ == "__main__":
    run_inventory_app()
