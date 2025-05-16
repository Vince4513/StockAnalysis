import sys
from pathlib import Path

# Add project root to PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parents[1]))

from financial_pipeline.interface.financial_data_interface import FinancialDataInterface

def run_streamlit_app(db_path: str | None = None):
    interface = FinancialDataInterface(db_path)
    interface.run()

if __name__ == "__main__":
    # db_path = "data/processed/production.db"
    run_streamlit_app(db_path=None)
