
import streamlit as st
import pandas as pd
from gspread_helper import load_inventory_from_gsheet, update_inventory_to_gsheet

def add_inventory(df):
    st.subheader("Add Inventory")

    category = st.selectbox("Category", df["Category"].unique())
    size = st.selectbox("Size", df[df["Category"] == category]["Size"].unique())
    item = st.selectbox("Item", df[(df["Category"] == category) & (df["Size"] == size)]["Item"].unique())

    idx = df[(df["Category"] == category) & (df["Size"] == size) & (df["Item"] == item)].index[0]
    packets_per_box = int(df.at[idx, "Packets_per_Box"])

    target = st.radio("Add to", ["Diesel_Engine", "Rack"], horizontal=True)
    unit = st.radio("Enter in", ["Box", "Packets/Nos"], horizontal=True)

    qty = st.number_input("Quantity", min_value=0, step=1)

    if st.button("Add"):
        if unit == "Box":
            packets = qty * packets_per_box
        else:
            packets = qty

        df.at[idx, target] += packets
        df.at[idx, "Total_Packets"] = df.at[idx, "Diesel_Engine"] + df.at[idx, "Rack"]

        update_inventory_to_gsheet(df)
        st.success(f"✅ Added {packets} packets to {target.replace('_', ' ')}")

def run_inventory_app():
    st.title("Inventory Management - Unique Agency")

    if "inventory" not in st.session_state:
        st.session_state.inventory = load_inventory_from_gsheet()

    df = st.session_state.inventory.copy()

    action = st.sidebar.radio("Choose Operation", ["Add Inventory", "View Inventory"])

    if action == "Add Inventory":
        add_inventory(df)
    elif action == "View Inventory":
        st.subheader("Current Inventory Status")
        df_display = df.copy()
        df_display["Low Status"] = df_display["Rack"].apply(lambda x: "LOW" if x < 10 else "")
        st.dataframe(df_display)

if __name__ == "__main__":
    run_inventory_app()
