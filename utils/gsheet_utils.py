from datetime import datetime
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import streamlit as st

# 🌐 Constants
GSHEET_SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]
CREDENTIALS_PATH = "config/birthday.json"
SPREADSHEET_NAME = "birthday"

def get_local_path():
    email = st.session_state.get("user_email", "default")
    safe_email = "".join(c if c.isalnum() else "_" for c in email)
    return f"sample_data/{safe_email}_data.xlsx"


class MockSheet:
    def __init__(self, df, title=None):
        self.df = df
        user = st.session_state.get("user_email", "admin").split("@")[0]
        self.title = title or f"{user}-{datetime.now().year}"

    def get_all_records(self):
        return self.df.to_dict(orient='records')

    def clear(self):
        pass

    def update(self, range_name, data):
        """Save updated data both in-memory and to Excel file."""
        try:
            if len(data) > 0:
                headers = data[0]
                values  = data[1:]
                self.df = pd.DataFrame(values, columns=headers)

                # ✅ FIX: create sample_data directory if it doesn't exist
                os.makedirs(os.path.dirname(get_local_path()), exist_ok=True)
                self.df.to_excel(get_local_path(), index=False)

                # ✅ FIX: also keep session_state in sync so Summary page is live
                st.session_state['live_df'] = self.df.copy()
                st.toast("💾 Data saved to local Excel file", icon="💾")
        except Exception as e:
            st.error(f"Failed to save local data: {e}")

    def append_row(self, row):
        pass


class MockSpreadsheet:
    def __init__(self, df):
        self.sheet = MockSheet(df)

    def worksheet(self, title):
        return self.sheet

    def worksheets(self):
        return [self.sheet]

    def add_worksheet(self, title, rows, cols):
        return self.sheet

    def open(self, name):
        return self


# ✅ Authentication & client initialization
def get_gspread_client():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, GSHEET_SCOPE)
    return gspread.authorize(creds)


def is_new_year_sheet_needed(spreadsheet):
    current_year = datetime.now().year
    user = st.session_state.get("user_email", "admin").split("@")[0]
    return f"{user}-{current_year}" not in [s.title for s in spreadsheet.worksheets()]


# 🆕 Create sheet for new year with header
def create_new_year_sheet(spreadsheet, sheet_title):
    sheet = spreadsheet.add_worksheet(title=sheet_title, rows="1000", cols="26")
    sheet.append_row(["date", "month", "credit", "credit_details", "debit", "debit_details", "category"])
    return sheet


# 📥 Load current year's data
def load_data_from_gsheet():
    # ✅ FIX: If an entry was just added (OCR/Voice), use the live df from session_state
    #         instead of re-reading the Excel file (which may not have flushed yet)
    if "live_df" in st.session_state and st.session_state["live_df"] is not None:
        df = st.session_state["live_df"].copy()
        spreadsheet = MockSpreadsheet(df)
        return df, spreadsheet.sheet, spreadsheet

    # If credentials missing or empty → use sample data (offline mode)
    if not os.path.exists(CREDENTIALS_PATH) or os.path.getsize(CREDENTIALS_PATH) < 10:
        if "sample_data_loaded" not in st.session_state:
            st.toast("⚠️ Using Local Sample Data (Offline Mode)", icon="📂")
            st.session_state["sample_data_loaded"] = True

        if os.path.exists(get_local_path()):
            try:
                df = pd.read_excel(get_local_path())
                df = df.fillna("")
                expected_cols = ["date", "month", "credit", "credit_details",
                                 "debit", "debit_details", "category"]
                for col in expected_cols:
                    if col not in df.columns:
                        df[col] = ""
                spreadsheet = MockSpreadsheet(df)
                worksheet   = spreadsheet.sheet
                return df, worksheet, spreadsheet
            except Exception as e:
                st.error(f"❌ Error loading sample data: {e}")
                pass
        
        # New account / No file yet -> initialize empty memory sheet safely
        expected_cols = ["date", "month", "credit", "credit_details", "debit", "debit_details", "category"]
        df = pd.DataFrame(columns=expected_cols)
        spreadsheet = MockSpreadsheet(df)
        return df, spreadsheet.sheet, spreadsheet

    try:
        client       = get_gspread_client()
        spreadsheet  = client.open(SPREADSHEET_NAME)
        user         = st.session_state.get("user_email", "admin").split("@")[0]
        sheet_title  = f"{user}-{datetime.now().year}"

        if is_new_year_sheet_needed(spreadsheet):
            worksheet = create_new_year_sheet(spreadsheet, sheet_title)
        else:
            worksheet = spreadsheet.worksheet(sheet_title)

        df = pd.DataFrame(worksheet.get_all_records())
        
        # ✅ Ensure columns exist even if sheet is empty
        expected_cols = ["date", "month", "credit", "credit_details", "debit", "debit_details", "category"]
        for col in expected_cols:
            if col not in df.columns:
                df[col] = 0 if col in ['credit', 'debit'] else ""
                
        return df, worksheet, spreadsheet
    except Exception as e:
        st.error(f"Connection Error: {e}. Switching to offline mode.")
        expected_cols = ["date", "month", "credit", "credit_details", "debit", "debit_details", "category"]
        if os.path.exists(get_local_path()):
            df = pd.read_excel(get_local_path()).fillna("")
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = 0 if col in ['credit', 'debit'] else ""
            spreadsheet = MockSpreadsheet(df)
            return df, spreadsheet.sheet, spreadsheet
            
        # New account safely bypassing network error
        df = pd.DataFrame(columns=expected_cols)
        spreadsheet = MockSpreadsheet(df)
        return df, spreadsheet.sheet, spreadsheet


# 🔄 Push updated DataFrame to Google Sheet / MockSheet
def update_data_to_gsheet(sheet, df):
    """
    Saves data to the sheet and ensures the local session state is in sync.
    """
    try:
        sheet.clear()
        data = [df.columns.tolist()] + df.values.tolist()
        sheet.update('A1', data)
        # Always keep session state in sync so the Summary page updates instantly
        st.session_state['live_df'] = df.copy()
    except Exception as e:
        st.error(f"Failed to update sheet: {e}")



# 📊 Load all yearly data from "test-" sheets
def load_yearly_data(spreadsheet):
    yearly_data = {}

    if isinstance(spreadsheet, MockSpreadsheet):
        # ✅ FIX: always use the latest in-memory df (reflects new entries)
        df = spreadsheet.sheet.df.copy()
        df['credit'] = pd.to_numeric(df.get('credit', 0), errors='coerce').fillna(0)
        df['debit']  = pd.to_numeric(df.get('debit',  0), errors='coerce').fillna(0)
        if 'year' not in df.columns:
            df['year'] = str(datetime.now().year)
        yearly_data[spreadsheet.sheet.title] = df
        return yearly_data

    for sheet in spreadsheet.worksheets():
        user = st.session_state.get("user_email", "admin").split("@")[0]
        if sheet.title.lower().startswith(user.lower() + "-"):
            df = pd.DataFrame(sheet.get_all_records())
            if not df.empty:
                df['year']   = sheet.title.split('-')[-1]
                df['credit'] = pd.to_numeric(df.get('credit', 0), errors='coerce').fillna(0)
                df['debit']  = pd.to_numeric(df.get('debit',  0), errors='coerce').fillna(0)
                yearly_data[sheet.title] = df
    return yearly_data

# 🗑️ Wipe All Data Function
def wipe_all_data(sheet):
    """Securely wipes all transaction history."""
    try:
        # Create fresh empty DataFrame with headers
        empty_df = pd.DataFrame(columns=["date", "month", "credit", "credit_details", "debit", "debit_details", "category"])
        
        # 1. Clear session state
        st.session_state['live_df'] = empty_df.copy()
        
        # 2. Update Sheet/Excel
        update_data_to_gsheet(sheet, empty_df)
        return True
    except Exception as e:
        st.error(f"Wipe failed: {e}")
        return False