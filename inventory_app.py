import streamlit as st
import pandas as pd
from gspread_helper import load_inventory_from_gsheet, update_inventory_to_gsheet

def run_inventory_app():
    st.title("🧮 Inventory Management")

    sheet_id = "1V61WCd-bGiLTwrdQKr1WccSIEZ570Ft9WLPdlxdiVJA"
    sheet_name = "inv_check"
    inv = load_inventory_from_gsheet(sheet_name)

    if 'inventory' not in st.session_state:
        st.session_state.inventory = inv.copy()

    inv = st.session_state.inventory

    st.subheader("Add Inventory")
    category_options = sorted(inv['Category'].dropna().unique())
    category = st.selectbox("Select Category", category_options)

    filtered_by_category = inv[inv["Category"] == category]
    if filtered_by_category.empty:
        st.warning("No items available for this category.")
        return

    size_options = sorted(filtered_by_category["Size"].dropna().unique())
    size = st.selectbox("Select Size", size_options)

    filtered_by_size = filtered_by_category[filtered_by_category["Size"] == size]
    if filtered_by_size.empty:
        st.warning("No items available for this size.")
        return

    item_options = sorted(filtered_by_size["Item"].dropna().unique())
    item = st.selectbox("Select Item", item_options)

    action = st.radio("Select Action", ["Add to Diesel Engine", "Move to Rack", "Subtract from Rack"])

    mode = st.radio("Select Unit", ["Box", "Packets/Nos"])
    quantity = st.number_input("Enter Quantity", min_value=1, step=1)

    if st.button("Submit"):
        idx = inv[(inv["Category"] == category) & (inv["Size"] == size) & (inv["Item"] == item)].index
        if idx.empty:
            st.error("Selected combination not found in inventory.")
            return

        idx = idx[0]

        try:
            packets_per_box = int(inv.at[idx, "Packets_per_Box"])
        except:
            st.error("Packets_per_Box value is missing or invalid.")
            return

        if mode == "Box":
            quantity *= packets_per_box

        if action == "Add to Diesel Engine":
            inv.at[idx, "Diesel_Engine"] = int(inv.at[idx, "Diesel_Engine"]) + quantity

        elif action == "Move to Rack":
            if inv.at[idx, "Diesel_Engine"] >= quantity:
                inv.at[idx, "Diesel_Engine"] -= quantity
                inv.at[idx, "Rack"] = int(inv.at[idx, "Rack"]) + quantity
            else:
                st.error("Not enough inventory in Diesel Engine.")
                return

        elif action == "Subtract from Rack":
            if inv.at[idx, "Rack"] >= quantity:
                inv.at[idx, "Rack"] -= quantity
            else:
                st.error("Not enough inventory in Rack.")
                return

        inv.at[idx, "Total_Packets"] = inv.at[idx, "Diesel_Engine"] + inv.at[idx, "Rack"]
        update_inventory_to_gsheet(sheet_name, inv)
        st.success("Inventory updated successfully.")

    if st.button("Show Inventory Status"):
        st.subheader("Current Inventory")
        display_inv = inv.copy()
        display_inv["Status"] = display_inv["Rack"].apply(lambda x: "🔴 LOW" if x < 10 else "🟢 OK")
        st.dataframe(display_inv)
