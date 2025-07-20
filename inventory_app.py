import streamlit as st
import pandas as pd
from gspread_helper import load_inventory_from_gsheet, update_inventory_to_gsheet

def run_inventory_app():
    st.title("🧮 Inventory Management")

    sheet_id = "1V61WCd-bGiLTwrdQKr1WccSIEZ570Ft9WLPdlxdiVJA"
    worksheet_name = "Sheet1"

    # Load inventory
    if "inventory" not in st.session_state:
        st.session_state.inventory = load_inventory_from_gsheet(sheet_id, worksheet_name)

    inv = st.session_state.inventory

    # Select Category
    category = st.selectbox("Select Category", sorted(inv["Category"].dropna().unique()))
    filtered_inv = inv[inv["Category"] == category]

    if not filtered_inv.empty:
        # Select Size
        size = st.selectbox("Select Size", sorted(filtered_inv["Size"].dropna().unique()))
        filtered_inv = filtered_inv[filtered_inv["Size"] == size]

        if not filtered_inv.empty:
            # Select Item
            item = st.selectbox("Select Item", sorted(filtered_inv["Item"].dropna().unique()))
            row_index = filtered_inv[filtered_inv["Item"] == item].index

            if not row_index.empty:
                index = row_index[0]
                st.write(f"### Selected Item: {item}")
                col1, col2 = st.columns(2)
                with col1:
                    add_type = st.radio("Add Format", ["Box", "Packets/Nos"])
                with col2:
                    location = st.radio("Add to", ["Diesel Engine", "Rack"])

                quantity = st.number_input("Enter quantity", min_value=0, step=1)
                if st.button("➕ Add"):
                    if add_type == "Box":
                        packets = quantity * int(inv.at[index, "Packets_per_Box"])
                    else:
                        packets = quantity

                    if location == "Diesel Engine":
                        inv.at[index, "Diesel_Engine"] += packets
                    else:
                        inv.at[index, "Rack"] += packets
                        inv.at[index, "Diesel_Engine"] -= packets

                    inv.at[index, "Total_Packets"] = inv.at[index, "Diesel_Engine"] + inv.at[index, "Rack"]
                    st.success("Inventory updated.")
                    update_inventory_to_gsheet(sheet_id, worksheet_name, inv)

                if st.button("➖ Subtract from Rack"):
                    if quantity > inv.at[index, "Rack"]:
                        st.error("Not enough stock in Rack.")
                    else:
                        inv.at[index, "Rack"] -= quantity
                        inv.at[index, "Total_Packets"] = inv.at[index, "Diesel_Engine"] + inv.at[index, "Rack"]
                        st.success("Stock subtracted from Rack.")
                        update_inventory_to_gsheet(sheet_id, worksheet_name, inv)

            else:
                st.warning("No item found for the selected size.")
        else:
            st.warning("No sizes available for the selected category.")
    else:
        st.warning("No inventory found for selected category.")

    if st.button("📊 Show Current Inventory"):
        st.dataframe(inv.style.apply(
            lambda row: ["background-color: red" if row["Rack"] < 10 else "" for _ in row],
            axis=1
        ))
