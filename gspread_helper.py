
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define the Google Sheet name
SHEET_NAME = "inv_check"

# Define the required scopes for accessing Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Function to authenticate and connect to the Google Sheet
def connect_to_gsheet(sheet_name):
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    return sheet

# Function to load inventory data into a pandas DataFrame
def load_inventory_from_gsheet(sheet_name=SHEET_NAME):
    sheet = connect_to_gsheet(sheet_name)
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

# Function to update the Google Sheet with the modified DataFrame
def update_inventory_to_gsheet(df, sheet_name=SHEET_NAME):
    sheet = connect_to_gsheet(sheet_name)
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
