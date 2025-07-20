
import streamlit as st
import pandas as pd
from gspread_helper import load_inventory_from_gsheet, update_inventory_to_gsheet

def run_inventory_app():
    st.title("Inventory Management")

    if "inventory" not in st.session_state:
        st.session_state.inventory = load_inventory_from_gsheet()

    inv = st.session_state.inventory

    st.subheader("Add Inventory")
    category = st.selectbox("Select Category", inv["Category"].unique())
    size = st.selectbox("Select Size", inv[inv["Category"] == category]["Size"].unique())
    item = st.selectbox("Select Item", inv[(inv["Category"] == category) & (inv["Size"] == size)]["Item"].unique())

    location = st.selectbox("Add to", ["Diesel_Engine", "Rack"])
    box = st.number_input("Number of Boxes", min_value=0, step=1)
    add_button = st.button("Add Inventory")

    if add_button and box > 0:
        idx = inv[(inv["Category"] == category) & (inv["Size"] == size) & (inv["Item"] == item)].index[0]
        packets_per_box = int(inv.at[idx, "Packets_per_Box"])
        new_packets = box * packets_per_box

        inv.at[idx, "Box"] += box
        inv.at[idx, "Packets/ Nos"] = inv.at[idx, "Box"] * packets_per_box
        inv.at[idx, location] += new_packets
        inv.at[idx, "Total_Packets"] = inv.at[idx, "Diesel_Engine"] + inv.at[idx, "Rack"]

        update_inventory_to_gsheet(inv)
        st.success(f"Added {new_packets} packets to {location} for item {item}.")

    st.subheader("Move from Diesel Engine to Rack")
    move_item = st.selectbox("Select Item to Move", inv[inv["Diesel_Engine"] > 0]["Item"].unique())
    move_count = st.number_input("Number of Packets to Move", min_value=0, step=1)
    move_button = st.button("Move")

    if move_button and move_item:
        idx = inv[inv["Item"] == move_item].index[0]
        if move_count <= inv.at[idx, "Diesel_Engine"]:
            inv.at[idx, "Diesel_Engine"] -= move_count
            inv.at[idx, "Rack"] += move_count
            inv.at[idx, "Total_Packets"] = inv.at[idx, "Diesel_Engine"] + inv.at[idx, "Rack"]
            update_inventory_to_gsheet(inv)
            st.success(f"Moved {move_count} packets from Diesel Engine to Rack.")
        else:
            st.error("Not enough packets in Diesel Engine.")

    st.subheader("Move from Rack to Shop (Subtract)")
    rack_item = st.selectbox("Select Item to Subtract", inv[inv["Rack"] > 0]["Item"].unique())
    subtract_count = st.number_input("Number of Packets to Subtract", min_value=0, step=1)
    subtract_button = st.button("Subtract from Rack")

    if subtract_button and rack_item:
        idx = inv[inv["Item"] == rack_item].index[0]
        if subtract_count <= inv.at[idx, "Rack"]:
            inv.at[idx, "Rack"] -= subtract_count
            inv.at[idx, "Total_Packets"] = inv.at[idx, "Diesel_Engine"] + inv.at[idx, "Rack"]
            update_inventory_to_gsheet(inv)
            st.success(f"Subtracted {subtract_count} packets from Rack.")
        else:
            st.error("Not enough packets in Rack.")

    st.subheader("Current Inventory")
    low_stock = inv["Rack"] < 10
    inv_display = inv.copy()
    inv_display["Status"] = ["LOW" if val else "OK" for val in low_stock]
    st.dataframe(inv_display.style.apply(lambda x: ['background-color: red' if v == "LOW" else '' for v in x], subset=['Status']))
