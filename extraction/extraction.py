# -*- coding: utf-8 -*- #
"""
Extraction of raw data
"""

from __future__ import annotations

import logging
import pandas as pd
from datetime import datetime

# ===========================================================================
# Constant and global variables
# ===========================================================================

logger = logging.getLogger(__name__)

# ===========================================================================
# Extraction Class
# ===========================================================================


class Extraction:
    """Extract interesting data from raw data"""

    def __init__(self, **kwargs) -> None:
        # Raw data 
        self.tickers_info = kwargs.get('tickers_info', None)
        self.balance_sheets = kwargs.get('balance_sheets', None)
        
        # Bronze data
        self.actual_share_price = None

        self.sales = None
        self.current_assets = None
        self.current_liabilities = None
        self.financial_debts = None
        self.nb_shares_issued = None
        self.equity = None
        self.intangible_assets = None

        self.net_income = None
        self.dividends = None
        self.net_earning_per_share = None
    # End def __init__

    # ===========================================================================
    # Magic Methods
    # ===========================================================================

    def __str__(self):
        return f"Extraction({self.sales})"

    # ===========================================================================
    # Public Methods
    # ===========================================================================

    def extract_all(self) -> None:
        for key in self.balance_sheets:
            logger.debug(f"Dataframe:\n{self.balance_sheets[key]}")

            self.current_assets = self.__extract_current_assets(self.balance_sheets[key])
            self.current_liabilities = self.__extract_current_liabilities(self.balance_sheets[key])
            self.equity = self.__extract_equity(self.balance_sheets[key])
            self.intangible_assets = self.__extract_goodwill(self.balance_sheets[key])
                

    # ===========================================================================
    # Private Methods
    # ===========================================================================

    def __extract_sales(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            # Filter the DataFrame to keep only rows where the index is in look_index
            result = df.loc['Sales']

        except Exception as e:
            result = None
        return result
    # End def __extract_sales

    def __extract_current_assets(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            # Current assets index names
            lookup_index = ['Current Assets', 'Other Current Assets']

            # Filter the DataFrame to keep only rows where the index is in look_index
            result = df.loc[lookup_index]

        except Exception as e:
            result = None
        return result
    # End def __extract_current_assets

    def __extract_long_term_debt(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            # Filter the DataFrame to keep only rows where the index is in look_index
            result = df.loc['Long Term Debt']

        except Exception as e:
            result = None
        return result
    # End def __extract_long_term_debt

    def __extract_current_liabilities(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            # Current liabilities index names
            lookup_index = ['Current Liabilities', 'Other Current Liabilities']
            
            # Filter the DataFrame to keep only rows where the index is in look_index
            result = df.loc[lookup_index]

        except Exception as e:
            result = None
        return result
    # End def __extract_current_liabilities

    def __extract_net_income(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            # Current liabilities index names
            lookup_index = ['Current Liabilities', 'Other Current Liabilities']
            
            # Filter the DataFrame to keep only rows where the index is in look_index
            result = df.loc[lookup_index]

        except Exception as e:
            result = None
        return result
    # End def __extract_net_income

    def __extract_dividends(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            # Current liabilities index names
            lookup_index = ['Current Liabilities', 'Other Current Liabilities']
            
            # Filter the DataFrame to keep only rows where the index is in look_index
            result = df.loc[lookup_index]

        except Exception as e:
            result = None
        return result
    # End def __extract_dividends

    def __extract_net_earning_per_share(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            # Current liabilities index names
            lookup_index = ['Current Liabilities', 'Other Current Liabilities']
            
            # Filter the DataFrame to keep only rows where the index is in look_index
            result = df.loc[lookup_index]

        except Exception as e:
            result = None
        return result
    # End def __extract_net_earning_per_share

    def __extract_equity(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            # Filter the DataFrame to keep only rows where the index is in look_index
            result = df.loc['Stockholders Equity']

        except Exception as e:
            result = None
        return result
    # End def __extract_equity

    def __extract_goodwill(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            # Filter the DataFrame to keep only rows where the index is in look_index
            result = df.loc['Goodwill And Other Intangible Assets']

        except Exception as e:
            result = None
        return result
    # End def __extract_goodwill
# End class Extraction