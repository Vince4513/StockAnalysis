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

def chrono(message: str = "") -> None:
    from datetime import datetime

    now = datetime.now()
    # now_str = now.strftime("%d-%m-%Y %H:%M:%s")
    print(f"{now} - {message}\n")
# End def chrono