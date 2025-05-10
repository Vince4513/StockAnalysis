import sys
from pathlib import Path

# Add project root to PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parents[1]))

from financial_pipeline.interface.financial_data_interface import run_streamlit_app

if __name__ == "__main__":
    run_streamlit_app()
