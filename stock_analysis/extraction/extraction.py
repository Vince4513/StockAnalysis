# -*- coding: utf-8 -*- #
"""
Extraction of raw data
"""

from __future__ import annotations

import logging
import pandas as pd
from typing import Iterator
from datetime import datetime

from stock_analysis.fresh_data.company import Company

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
    # End def __init__

    # ===========================================================================
    # Magic Methods
    # ===========================================================================

    def __str__(self):
        return f"Extraction({datetime.now()} - {list(self.tickers_info.keys())})"

    # ===========================================================================
    # Public Methods
    # ===========================================================================

    def extract_all(self) -> Iterator[Company]:
        # Extract data to company class
        for key in self.balance_sheets:
            logger.debug(f"Dataframe:\n{self.balance_sheets[key]}")

            company = Company(
                actual_share_price = 1,
                sales              = self.__extract_sales(),
                nb_shares_issued   = self.__extract_nb_shares_issued(key),

                # Balance sheet information
                current_assets      = self.__extract_current_assets(self.balance_sheets[key]),
                current_liabilities = self.__extract_current_liabilities(self.balance_sheets[key]), 
                financial_debts     = self.__extract_long_term_debt(self.tickers_info[key]),
                equity              = self.__extract_equity(self.balance_sheets[key]),
                intangible_assets   = self.__extract_goodwill(self.balance_sheets[key]), 

                # Arrays
                net_income=0,
                dividends=0,   
                net_earning_per_share=0
            )

            # Return company one by one
            yield company
    # End def extract_all

    def as_rule_dataframe(self):
        pass
    # End def as_rule_dataframe

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

    def __extract_long_term_debt(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            # Filter the DataFrame to keep only rows where the index is in look_index
            result = df.loc['Long Term Debt']

        except Exception as e:
            result = None
        return result
    # End def __extract_long_term_debt

    def __extract_nb_shares_issued(self, company: str) -> int:
        return self.tickers_info[company]['nb_shares']
    # End def __extract_long_term_debt

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

    def __extract_net_income(self, df: pd.DataFrame) -> pd.DataFrame:
        pass
    # End def __extract_net_income

    def __extract_dividends(self, df: pd.DataFrame) -> pd.DataFrame:
        pass
    # End def __extract_dividends

    def __extract_net_earning_per_share(self, df: pd.DataFrame) -> pd.DataFrame:
        pass
    # End def __extract_net_earning_per_share
# End class Extraction

def main():
    Extraction()

if __name__ == "__main__":
    main()