import os
import json

from financial_pipeline.importer.financial_data_importer import FinancialDataImporter
from financial_pipeline.cleaner.financial_data_cleaner import FinancialDataCleaner
from financial_pipeline.utils.helpers import insert_cleaned_financials


def run():
    importer = FinancialDataImporter()
    cleaner = FinancialDataCleaner()

    # Example: load a local raw file (e.g., TTE.PA.json)
    with open(os.path.join(importer.data_path, "TTE.PA.json"), "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    cleaned_rows = cleaner.extract_all(raw_data, company_name="TTE.PA")
    insert_cleaned_financials(cleaned_rows)
# End def run

def run_all():
    importer = FinancialDataImporter()
    cleaner = FinancialDataCleaner()

    importer.retrieve_data()

    raw_dir = importer.data_path
    json_files = [f for f in os.listdir(raw_dir) if f.endswith(".json")]
    json_files.remove("yh_tickers.json")

    cpt: int = 0
    all_rows = []
    for filename in json_files:
        path = os.path.join(raw_dir, filename)

        try:
            with open(path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
            
            company_name = filename.replace(".json", "")
            cleaned_rows = cleaner.extract_all(raw_data, company_name)
            all_rows.extend(cleaned_rows)

            print(f"[✓] Cleaned and loaded {cpt+1}: {filename}", end="\r")
            cpt += 1
        except Exception as e:
            print(f"[✗] Failed to process {filename}: {e}")

    insert_cleaned_financials(all_rows)
# End def run_all

if __name__ == "__main__":
    run_all()