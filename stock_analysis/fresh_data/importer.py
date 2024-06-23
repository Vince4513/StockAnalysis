# -*- coding: utf-8 -*- #
"""
Importer of data
"""

from __future__ import annotations

import ast
import logging
import pandas as pd
import yfinance as yf
from tqdm import tqdm
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

        # Yahoo tickers
        self.tickers_name : dict | None = None

        # API info
        self.tickers_info     : dict | None = None
        self.income_statement : dict | None = None
        self.balance_sheets   : dict | None = None
    # End def __init__

    # ===========================================================================
    # Public methods
    # ===========================================================================

    # Define the function to read the dictionary from a text file
    def retrieve_tickers(self, filename) -> None:
        # with open(filename, 'r', encoding='utf-8') as file:
        #     content = file.read()
        #     self.tickers_name = ast.literal_eval(content)
        self.tickers_name = {'TTE.PA': 'Total Energies', 
                             'AI.PA' : 'Air Liquide',
                             'SAN.PA': 'Sanofi',
                             'DG.PA' : 'Vinci',
                             'OR.PA': 'L\'Oréal',
                             'SU.PA': 'Schneider Electric'}
    # End def retrieve tickers

    def retrieve_data(self):
        if self.tickers_name == None:
            raise ValueError(f"Expected tickers, but got none")

        # try:
        tickers = [yf.Ticker(ticker) for ticker in list(self.tickers_name.keys())]
        # except Exception as e:
            # logger.debug(f"Ticker not found: {e}")

        inc_statement = {}
        bal_sheet     = {}
        ticker_info   = {}
        for ticker in tqdm(tickers):
            try:
                # Filter by exchange / market place
                # exchanges = ['PAR']
                # if ticker.fast_info.exchange in exchanges: 
                if ticker.ticker.endswith('.PA'):
                    print(f"{ticker.ticker}", end='\r') #{dir(ticker)}
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
            
                    # Income statement (Compte de résultat)
                    inc_statement[ticker.ticker] = ticker.incomestmt

                    # Balance sheets (Bilan comptable)
                    bal_sheet[ticker.ticker] = ticker.balancesheet                    
            
            except KeyError:
                continue
            except Exception:
                continue

        self.tickers_info = ticker_info
        self.income_statement = inc_statement
        self.balance_sheets = bal_sheet
    # End def retrieve_data
    
    def to_database(self):
        e = Extraction(
            tickers_info   = self.tickers_info, 
            income_statement = self.income_statement,
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