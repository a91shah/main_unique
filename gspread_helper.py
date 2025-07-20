import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

def connect_to_gsheet(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    return sheet

def load_inventory_from_gsheet(sheet_name="inv_check"):
    sheet = connect_to_gsheet(sheet_name)
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def save_inventory_to_gsheet(df, sheet_name="inv_check"):
    sheet = connect_to_gsheet(sheet_name)
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
