import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

def connect_to_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope
    )
    client = gspread.authorize(creds)
    return client

def load_inventory_from_gsheet(sheet_id, worksheet_name):
    client = connect_to_gsheet()
    sheet = client.open_by_key(sheet_id).worksheet(worksheet_name)
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def update_inventory_to_gsheet(sheet_id, worksheet_name, df):
    client = connect_to_gsheet()
    sheet = client.open_by_key(sheet_id).worksheet(worksheet_name)
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
