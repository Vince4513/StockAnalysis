# -*- coding: utf-8 -*- #
"""
Cleaning of raw data
"""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd
from typing import Iterator
from datetime import datetime

from archive.company import Company

# ===========================================================================
# Constant and global variables
# ===========================================================================

logger = logging.getLogger(__name__)

# ===========================================================================
# FinancialDataCleaner Class
# ===========================================================================


class FinancialDataCleaner:
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
            
            try:
                # Extract the relevant information
                actual_share_price  = self.tickers_info[company]['share']
                sales               = self.__extract_sales(self.income_statement[company])
                nb_shares_issued    = self.tickers_info[company]['nb_shares']
                current_assets      = self.__extract_current_assets(self.balance_sheets[company])
                current_liabilities = self.__extract_current_liabilities(self.balance_sheets[company])
                financial_debts     = self.__extract_long_term_debt(self.balance_sheets[company])
                equity              = self.__extract_equity(self.balance_sheets[company])
                intangible_assets   = self.__extract_goodwill(self.balance_sheets[company])
                net_income          = self.__extract_net_income(self.income_statement[company])
                dividends           = self.__extract_dividends(self.tickers_info[company]['dividends'])
                net_earning_per_share = self.__extract_net_earning_per_share(self.income_statement[company])

                # Check if any required information is None in single variable
                if any(info is None for info in [
                    actual_share_price, sales, nb_shares_issued, current_assets, 
                    current_liabilities, financial_debts, equity, intangible_assets]):
                    print(f"Skipping {company} due to missing data.")
                    continue  # Skip to the next company if any info is None
                
                # Check if any required information is None in pandas dataframe
                if any(info.isnull().sum() > 0 for info in [net_income, dividends, net_earning_per_share]):
                    print(f"Skipping {company} due to missing data.")
                    continue  # Skip to the next company if any info is None

                # If all information is available, create the company object
                company = Company(
                    name                = company,
                    actual_share_price  = actual_share_price,
                    sales               = sales,
                    nb_shares_issued    = nb_shares_issued,

                    # Balance sheet information
                    current_assets      = current_assets,
                    current_liabilities = current_liabilities,
                    financial_debts     = financial_debts,
                    equity              = equity,
                    intangible_assets   = intangible_assets,
                    
                    # Arrays
                    net_income          = net_income,
                    dividends           = dividends,
                    net_earning_per_share = net_earning_per_share
                )

                # Return company one by one
                yield company
                
            except KeyError as e:
                print(f"KeyError for company {company}: {e}")
            except Exception as e:
                print(f"Error processing company {company}: {e}")
    # End def extract_all

    # ===========================================================================
    # Private Methods
    # ===========================================================================

    def __extract_sales(self,  df: pd.DataFrame) -> float | None:
        try:
            # Current assets index names
            lookup_index = ['Operating Revenue']

            # Filter the DataFrame to keep only rows where the index is in look_index
            filt_df = df.loc[lookup_index]

            # Take only last year and we have only one row 
            result = sum(filt_df.iloc[:, 0])

        except Exception as e:
            result = None
        return result
    # End def __extract_sales

    def __extract_current_assets(self, df: pd.DataFrame) -> float | None:
        try:
            # Current assets index names
            lookup_index = ['Current Assets', 'Other Current Assets']

            # Filter the DataFrame to keep only rows where the index is in look_index
            filt_df = df.loc[lookup_index]
            
            # Take only last year and we sum the 2 rows
            result = sum(filt_df.iloc[:, 0])

        except Exception as e:
            result = None
        return result
    # End def __extract_current_assets

    def __extract_current_liabilities(self, df: pd.DataFrame) -> float | None:
        try:
            # Current liabilities index names
            lookup_index = ['Current Liabilities', 'Other Current Liabilities']
            
            # Filter the DataFrame to keep only rows where the index is in look_index
            filt_df = df.loc[lookup_index]
            
            # Take only last year and we sum the 2 rows
            result = sum(filt_df.iloc[:, 0])

        except Exception as e:
            result = None
        return result
    # End def __extract_current_liabilities

    def __extract_long_term_debt(self, df: pd.DataFrame) -> float | None:
        try:
            # Financial Long term debt index names
            # 'Long Term Debt' similar to 'Long Term Debt And Capital Lease Obligation' 
            lookup_index = ['Derivative Product Liabilities', 'Long Term Debt And Capital Lease Obligation']

            # Filter the DataFrame to keep only rows where the index is in look_index
            filt_df = df.loc[lookup_index]
            
            # Take only last year and we sum the 2 rows
            result = sum(filt_df.iloc[:, 0])

        except Exception:
            try:
                filt_df = df.loc['Long Term Debt And Capital Lease Obligation']
                
                # Take only last year and we sum the 2 rows
                result = sum(filt_df.iloc[:, 0])
            
            except Exception:
                result = None

        return result
    # End def __extract_long_term_debt

    def __extract_equity(self, df: pd.DataFrame) -> float | None:
        try:
            lookup_index = ['Stockholders Equity']
            
            # Filter the DataFrame to keep only rows where the index is in look_index
            filt_df = df.loc[lookup_index]
            
            # Take only last year and we sum the 2 rows
            result = sum(filt_df.iloc[:, 0])

        except Exception as e:
            result = None
        return result
    # End def __extract_equity

    def __extract_goodwill(self, df: pd.DataFrame) -> float | None:
        try:
            lookup_index = ['Goodwill And Other Intangible Assets']

            # Filter the DataFrame to keep only rows where the index is in look_index
            filt_df = df.loc[lookup_index]
            
            # Take only last year and we sum the 2 rows
            result = sum(filt_df.iloc[:, 0])

        except Exception as e:
            result = None
        return result
    # End def __extract_goodwill

    def __extract_net_income(self, df: pd.DataFrame) -> pd.DataFrame | None:
        try:
            # Filter the DataFrame to keep only rows where the index is in look_index
            # 'Net Income' possible as well but not same values
            result = df.loc['Net Income Continuous Operations']

        except Exception as e:
            result = None
        return result
    # End def __extract_net_income

    def __extract_dividends(self, df: pd.DataFrame) -> pd.DataFrame | None:
        try:
            # Filter the DataFrame to keep only rows where the index is in look_index
            # 'Net Income' possible as well but not same values
            
            # Sum the values per year
            df_yearly_sum = df.resample('YE').sum()

        except Exception as e:
            df_yearly_sum = None
        return df_yearly_sum
    # End def __extract_dividends

    def __extract_net_earning_per_share(self, df: pd.DataFrame) -> pd.DataFrame | None:
        try:
            # 'Diluted EPS' 
            result = df.loc['Basic EPS']

        except Exception as e:
            result = None
        return result
    # End def __extract_net_earning_per_share
# End class Extraction

if __name__ == "__main__":
    FinancialDataCleaner()