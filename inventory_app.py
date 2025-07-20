
import streamlit as st
import pandas as pd
from gspread_helper import load_inventory_from_gsheet, update_inventory_to_gsheet

def run_inventory_app():
    st.title("Inventory Management - Diesel Engine")

    # Load inventory from Google Sheet
    if "inventory" not in st.session_state:
        st.session_state.inventory = load_inventory_from_gsheet()

    inv = st.session_state.inventory

    # Selection UI
    category = st.selectbox("Select Category", sorted(inv["Category"].unique()))
    # Filter by category and show Size dropdown only if available
filtered_by_cat = inv[inv["Category"] == category]
if not filtered_by_cat.empty:
    size = st.selectbox("Select Size", sorted(filtered_by_cat["Size"].dropna().unique()))
    filtered_by_size = filtered_by_cat[filtered_by_cat["Size"] == size]

    if not filtered_by_size.empty:
        item = st.selectbox("Select Item", sorted(filtered_by_size["Item"].dropna().unique()))
    else:
        st.warning("No items found for this size.")
        return
else:
    st.warning("No sizes found for this category.")
    return & (inv["Size"] == size)]["Item"].unique()))
    idx = inv[(inv["Category"] == category) & (inv["Size"] == size) & (inv["Item"] == item)].index[0]

    st.markdown("---")
    st.subheader("Add Inventory to Diesel Engine")
    add_type = st.radio("Add as", ["Box", "Packets/Nos"], horizontal=True)
    add_value = st.number_input(f"Enter {add_type} to Add", min_value=0, step=1)

    if st.button("Add to Diesel Engine"):
        if add_type == "Box":
            packets = add_value * inv.at[idx, "Packets_per_Box"]
        else:
            packets = add_value
        inv.at[idx, "Diesel_Engine"] += packets
        inv.at[idx, "Total_Packets"] = inv.at[idx, "Diesel_Engine"] + inv.at[idx, "Rack"]
        update_inventory_to_gsheet(inv)
        st.success("Inventory updated in Diesel Engine")

    st.markdown("---")
    st.subheader("Move Inventory from Diesel Engine to Rack")
    move_to_rack = st.number_input("Enter Packets to Move to Rack", min_value=0, step=1, key="move")
    if st.button("Move to Rack"):
        if move_to_rack <= inv.at[idx, "Diesel_Engine"]:
            inv.at[idx, "Diesel_Engine"] -= move_to_rack
            inv.at[idx, "Rack"] += move_to_rack
            inv.at[idx, "Total_Packets"] = inv.at[idx, "Diesel_Engine"] + inv.at[idx, "Rack"]
            update_inventory_to_gsheet(inv)
            st.success("Moved to Rack")
        else:
            st.error("Not enough packets in Diesel Engine")

    st.markdown("---")
    st.subheader("Subtract from Rack (Moved to Shop)")
    remove_from_rack = st.number_input("Enter Packets to Subtract from Rack", min_value=0, step=1, key="remove")
    if st.button("Subtract from Rack"):
        if remove_from_rack <= inv.at[idx, "Rack"]:
            inv.at[idx, "Rack"] -= remove_from_rack
            inv.at[idx, "Total_Packets"] = inv.at[idx, "Diesel_Engine"] + inv.at[idx, "Rack"]
            update_inventory_to_gsheet(inv)
            st.success("Subtracted from Rack")
        else:
            st.error("Not enough packets in Rack")

    st.markdown("---")
    if st.button("Show Inventory Status"):
        st.subheader("Current Inventory Status")
        df = inv.copy()
        df["Status"] = df["Rack"].apply(lambda x: "LOW" if x < 10 else "OK")
        st.dataframe(df.style.applymap(lambda val: "color: red;" if val == "LOW" else "", subset=["Status"]))
