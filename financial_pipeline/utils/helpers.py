import ctypes
import platform
import subprocess
import pandas as pd
from typing import List, Dict

from financial_pipeline.storage.company_storage import CompanyStorage


def insert_cleaned_financials(rows: List[Dict], db_path=None):
    """
    Insert a list of cleaned financial rows into the SQLite database.
    Each row should include all required fields (name, year, financial metrics).
    """
    db = CompanyStorage(db_path)

    

    for row in rows:
        name = row.pop("name")
        year = row.pop("year")

        keys_to_extract = ["country", "phone", "website", "industry", "sector", "region", "full_exchange_name", 
                           "exchange_timezone", "isin", "full_time_employees"]
        
        companies_row = {key: row.pop(key) for key in keys_to_extract}
        
        # Ensure company exists
        db.add_company(name, **companies_row)
        
        # Insert or update the financial data
        db.update_financials(name, year, **row)

    db.close()
# End def insert_cleaned_financials

def get_safe_values(row, keys: List[str]) -> tuple[bool, Dict]:
    """
    Safely extract values from a row and check for missing (None or NaN) data.

    Returns:
        (has_all_data: bool, values: list or dict)
    """
    values = {}
    for key in keys:
        val = row.get(key)
        if pd.isna(val):
            return False, {}
        values[key] = val
    return True, values
# End def get_safe_values

def chrono(message: str = "") -> None:
    from datetime import datetime

    now = datetime.now()
    # now_str = now.strftime("%d-%m-%Y %H:%M:%s")
    print(f"{now} - {message}\n")
# End def chrono

def prevent_sleep():
    os_name = platform.system()

    if os_name == "Windows":
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
    elif os_name == "Darwin":
        # Start caffeinate in background
        return subprocess.Popen(["caffeinate"])
    elif os_name == "Linux":
        # Start systemd-inhibit in background
        return subprocess.Popen(["systemd-inhibit", "--why=prevent sleep", "--mode=block", "sleep", "infinity"])
# End def prevent_sleep

def allow_sleep(process=None):
    os_name = platform.system()

    if os_name == "Windows":
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
    elif process:
        process.terminate()
# End def allow_sleep