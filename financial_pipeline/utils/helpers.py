from typing import List, Dict
from financial_pipeline.storage.company_storage import CompanyStorage


def insert_cleaned_financials(rows: List[Dict], db_path="financials.db"):
    """
    Insert a list of cleaned financial rows into the SQLite database.
    Each row should include all required fields (name, year, financial metrics).
    """
    db = CompanyStorage(db_path)

    for row in rows:
        name = row.pop("name")
        year = row.pop("year")
        
        # Ensure company exists
        db.add_company(name)
        
        # Insert or update the financial data
        db.update_financials(name, year, **row)

    db.close()
# End def insert_cleaned_financials