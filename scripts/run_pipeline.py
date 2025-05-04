from financial_pipeline.importer.financial_data_importer import FinancialDataImporter
from financial_pipeline.cleaner.financial_data_cleaner import FinancialDataCleaner
from financial_pipeline.storage.company_storage import CompanyStorage

def run():
    raw_data = FinancialDataImporter().load_data()
    cleaned_data = FinancialDataCleaner().clean(raw_data)

    db = CompanyStorage()
    for entry in cleaned_data:
        db.add_company(entry['name'], entry.get('industry'), entry.get('country'))
        db.update_financials(entry['name'], entry['year'], **entry['financials'])
    db.close()

if __name__ == "__main__":
    run()