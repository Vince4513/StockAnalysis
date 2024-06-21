# -*- coding: utf-8 -*- #
"""
Importer of data
"""

from __future__ import annotations

import logging
import pandas as pd
import yfinance as yf

# ===========================================================================
# Constant and global variables
# ===========================================================================

logger = logging.getLogger(__name__)

# ===========================================================================
# Importer Class
# ===========================================================================

class StockDataImporter:
    """Import the data from Internet"""

    def __init__(self) -> None:
        self.tickers_info = None
        self.balance_sheets = None
    # End def __init__

    # ===========================================================================
    # Properties
    # ===========================================================================

    # @property
    # def balance_sheets(self) -> list[dict]:
    #     return self.balance_sheets


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
    
    def extract_data(self, balance_sheets: dict[pd.DataFrame]):
        for key in balance_sheets:
            logger.debug(f"Dataframe:\n{balance_sheets[key]}")

            p = self.__extract_from_balance_sheet(balance_sheets[key])
            logger.info(f"\n{p}\n")
    # ===========================================================================
    # Private methods
    # ===========================================================================

    def __extract_from_balance_sheet(self, df: pd.DataFrame) -> pd.DataFrame:
        # Assuming df is your DataFrame and strings is a list of strings you want to search for
        lookup_index = [
            # 'Sales',
            'Current Assets', #
            'Other Current Assets', #
            'Long Term Debt', #
            'Current Liabilities', #
            'Other Current Liabilities', #
            # 'Net Income',
            # 'Dividends',
            # 'Net Earnings per Share',
            'Stockholders Equity', #'Shareholders equity',
            'Goodwill And Other Intangible Assets' #
        ]

        try:
            # Filter the DataFrame to keep only rows where the index is in look_index
            result = df.loc[lookup_index]
            
            return result
        
        except Exception as e:
            print(e)
    # End def __extract_from_balance_sheet
    
# End class StockDataImporter