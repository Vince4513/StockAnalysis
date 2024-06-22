# -*- coding: utf-8 -*- #
"""
Importer of data
"""

from __future__ import annotations

import logging
import pandas as pd
import yfinance as yf
from pathlib import Path

from extraction.extraction import Extraction
from fresh_data.storage import CompanyStorage

# ===========================================================================
# Constant and global variables
# ===========================================================================

logger = logging.getLogger(__name__)

# ===========================================================================
# Importer Class
# ===========================================================================

class StockDataImporter:
    """Import the data from Internet"""

    def __init__(self, db_path: str | Path) -> None:
        
        self.datastore = CompanyStorage(db_path)
        self.datastore.clear()

        # API info
        self.tickers_info = None
        self.balance_sheets = None
    # End def __init__

    # ===========================================================================
    # Public methods
    # ===========================================================================

    def retrieve_data(self, tickers: list[str] | None):
        if tickers == None:
            raise ValueError(f"Expected tickers, but got none")

        tickers = [yf.Ticker(ticker) for ticker in tickers]

        bs = {}
        ticker_info = {}
        for ticker in tickers:

            # Filter by exchange / market place
            exchanges = ['PAR']
            if ticker.fast_info.exchange in exchanges: 
                # Get financial data
                ticker_info[ticker.ticker] = {
                    'ISIN': ticker.isin,
                    'share': ticker.fast_info.last_price,
                    'market_cap': ticker.fast_info.market_cap,
                    'nb_shares': ticker.fast_info.shares,
                    'dividends': ticker.dividends,
                    'financials': ticker.financials, 
                    'exchange': ticker.fast_info.exchange
                }
                
                # Balance sheets
                bs[ticker.ticker] = ticker.balancesheet

        self.tickers_info = ticker_info
        self.balance_sheets = bs
    # End def retrieve_data
    
    def to_database(self):
        e = Extraction(
            tickers_info   = self.tickers_info, 
            balance_sheets = self.balance_sheets
        )
    
        for index, company in enumerate(e.extract_all()):
            self.datastore.add_company(company)
            print(f"{index} - {company}")
        # End for index, company

        n_company = len(self.datastore)
        print(f"Imported {n_company} companies.")
    # End def to_database        

    # ===========================================================================
    # Private methods
    # ===========================================================================    
# End class StockDataImporter