import streamlit as st
import pandas as pd
from gspread_helper import load_inventory_from_gsheet, update_inventory_to_gsheet

def run_inventory_app():
    st.title("🧮 Inventory Management")

    sheet_id = "1V61WCd-bGiLTwrdQKr1WccSIEZ570Ft9WLPdlxdiVJA"
    sheet_name = "Sheet1"
    inv = load_inventory_from_gsheet(sheet_id, sheet_name)

    if inv.empty or "Category" not in inv.columns:
        st.warning("Inventory data is empty or missing 'Category' column.")
        return

    category = st.selectbox("Select Category", sorted(inv["Category"].dropna().unique()))
    filtered_inv = inv[inv["Category"] == category]

    if filtered_inv.empty or "Size" not in filtered_inv.columns:
        st.warning("No sizes found for this category.")
        return

    size = st.selectbox("Select Size", sorted(filtered_inv["Size"].dropna().unique()))
    filtered_inv = filtered_inv[filtered_inv["Size"] == size]

    if filtered_inv.empty or "Item" not in filtered_inv.columns:
        st.warning("No items found for this size.")
        return

    item = st.selectbox("Select Item", sorted(filtered_inv["Item"].dropna().unique()))
    entry = filtered_inv[(filtered_inv["Item"] == item)].copy()

    if entry.empty:
        st.warning("No matching inventory item found.")
        return

    box = st.number_input("Enter Box", min_value=0, step=1)
    packets = st.number_input("Or Enter Packets/Nos", min_value=0, step=1)

    add_btn = st.button("➕ Add to Diesel Engine")
    move_btn = st.button("📦 Move to Rack")
    subtract_btn = st.button("➖ Subtract from Rack")
    show_btn = st.button("📊 Show Current Inventory")

    idx = entry.index[0]
    packets_per_box = int(entry.at[idx, "Packets_per_Box"]) if pd.notna(entry.at[idx, "Packets_per_Box"]) else 0

    if add_btn:
        total_packets = packets + box * packets_per_box
        inv.at[idx, "Diesel_Engine"] = int(inv.at[idx, "Diesel_Engine"]) + total_packets
        inv.at[idx, "Total_Packets"] = int(inv.at[idx, "Diesel_Engine"]) + int(inv.at[idx, "Rack"])
        update_inventory_to_gsheet(sheet_id, sheet_name, inv)
        st.success(f"Added {total_packets} packets to Diesel Engine.")

    if move_btn:
        move_qty = st.number_input("Move how many packets to Rack?", min_value=0, step=1)
        if move_qty > int(inv.at[idx, "Diesel_Engine"]):
            st.error("Not enough packets in Diesel Engine.")
        else:
            inv.at[idx, "Diesel_Engine"] -= move_qty
            inv.at[idx, "Rack"] += move_qty
            inv.at[idx, "Total_Packets"] = int(inv.at[idx, "Diesel_Engine"]) + int(inv.at[idx, "Rack"])
            update_inventory_to_gsheet(sheet_id, sheet_name, inv)
            st.success(f"Moved {move_qty} packets to Rack.")

    if subtract_btn:
        sub_qty = st.number_input("Subtract how many packets from Rack?", min_value=0, step=1)
        if sub_qty > int(inv.at[idx, "Rack"]):
            st.error("Not enough packets in Rack.")
        else:
            inv.at[idx, "Rack"] -= sub_qty
            inv.at[idx, "Total_Packets"] = int(inv.at[idx, "Diesel_Engine"]) + int(inv.at[idx, "Rack"])
            update_inventory_to_gsheet(sheet_id, sheet_name, inv)
            st.success(f"Subtracted {sub_qty} packets from Rack.")

    if show_btn:
        st.subheader("📋 Current Inventory Status")
        st.dataframe(inv[["Category", "Size", "Item", "Diesel_Engine", "Rack", "Total_Packets"]])
