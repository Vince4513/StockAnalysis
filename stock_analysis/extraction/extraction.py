# -*- coding: utf-8 -*- #
"""
Extraction of raw data
"""

from __future__ import annotations

import logging
import pandas as pd
from typing import Iterator
from datetime import datetime

from fresh_data.company import Company

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
        self.income_statement = kwargs.get('income_statement', None)
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
        for company in self.tickers_info:
            logger.debug(f"Income statement:\n{self.income_statement[company]}")
            logger.debug(f"Balance sheet   :\n{self.balance_sheets[company].to_string()}")
            
            company = Company(
                name = company,
                actual_share_price = self.tickers_info[company]['share'],
                sales              = self.__extract_sales(self.income_statement[company]),
                nb_shares_issued   = self.tickers_info[company]['nb_shares'],

                # Balance sheet information
                current_assets      = self.__extract_current_assets(self.balance_sheets[company]),
                current_liabilities = self.__extract_current_liabilities(self.balance_sheets[company]), 
                financial_debts     = self.__extract_long_term_debt(self.balance_sheets[company]),
                equity              = self.__extract_equity(self.balance_sheets[company]),
                intangible_assets   = self.__extract_goodwill(self.balance_sheets[company]), 

                # Arrays
                net_income            = self.__extract_net_income(self.income_statement[company]),
                dividends             = self.tickers_info[company]['dividends'],   
                net_earning_per_share = self.__extract_net_earning_per_share(self.income_statement[company])
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

    def __extract_sales(self,  df: pd.DataFrame) -> None:
        try:
            # Current assets index names
            lookup_index = ['Operating Revenue']

            # Filter the DataFrame to keep only rows where the index is in look_index
            result = df.loc[lookup_index]

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
            # Financial Long term debt index names
            # 'Long Term Debt' similar to 'Long Term Debt And Capital Lease Obligation' 
            lookup_index = ['Derivative Product Liabilities', 'Long Term Debt And Capital Lease Obligation']

            # Filter the DataFrame to keep only rows where the index is in look_index
            result = df.loc[lookup_index]

        except Exception:
            try:
                result = df.loc['Long Term Debt And Capital Lease Obligation']
            except Exception:
                result = None

        return result
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
        try:
            # Filter the DataFrame to keep only rows where the index is in look_index
            # 'Net Income' possible as well but not same values
            result = df.loc['Net Income Continuous Operations']

        except Exception as e:
            result = None
        return result
    # End def __extract_net_income

    def __extract_dividends(self, df: pd.DataFrame) -> pd.DataFrame:
        pass
    # End def __extract_dividends

    def __extract_net_earning_per_share(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            # 'Diluted EPS' 
            result = df.loc['Basic EPS']

        except Exception as e:
            result = None
        return result
    # End def __extract_net_earning_per_share
# End class Extraction

def main():
    Extraction()

if __name__ == "__main__":
    main()