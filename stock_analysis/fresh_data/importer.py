# -*- coding: utf-8 -*- #
"""
Importer of data
"""

from __future__ import annotations

import json
import chardet
import logging
import numpy as np
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
    def retrieve_tickers(self, filename, dev=False) -> None:
        """Returns the ticker from json file under a dictionnary format

        Args:
            filename (str | Path): Path to load the file 

        Returns:
            dict: Dictionnary with ticker as key and name of the company as the value
        """

        # Allows to load a few companies and test further functions
        if dev == True:
            self.tickers_name = {
                'TTE.PA': 'Total Energies', 
                'AI.PA' : 'Air Liquide',
                'SAN.PA': 'Sanofi',
                'DG.PA' : 'Vinci',
                'OR.PA': 'L\'Oréal',
                'SU.PA': 'Schneider Electric'
            }
        # Load tickers from the json file
        else:
            encoding = self._detect_encoding(filename)
            with open(filename, 'r', encoding=encoding) as file:
                content = file.read()
                dictionary = json.loads(content)

                self.tickers_name =  dictionary
    # End def retrieve tickers

    def retrieve_data(self):
        if self.tickers_name == None:
            raise ValueError(f"Expected tickers, but got none")
        
        # Select the tickers to add based on filters
        tickers_to_add = [ticker for ticker in list(self.tickers_name.keys()) if ticker.endswith('.PA')]
        # try:
        tickers = [yf.Ticker(ticker) for ticker in tickers_to_add]
        # except Exception as e:
            # logger.debug(f"Ticker not found: {e}")

        inc_statement = {}
        bal_sheet     = {}
        ticker_info   = {}
        cptr = 0
        for ticker in tickers:
            cptr += 1
            try:
                print(f"{cptr} - {ticker.ticker}", end='\r')
                
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
            # Check if the company exists in the database
            if self.datastore.is_company(company):
                self.datastore.update_company(company)
                print(f"Update - {index} - {company}")

            else:
                self.datastore.add_company(company)
                print(f"Add - {index} - {company}")
        # End for index, company

        n_company = len(self.datastore)
        print(f"Imported {n_company} companies.")
    # End def to_database        

    def as_rule_dataframe(self) -> pd.DataFrame:
        """Take all companies' data and convert them in a dataframe

        Returns:
            pd.DataFrame: Dataframe with a column per company
        """
        rule_df = pd.DataFrame()

        # Define a function to safely get dataframe values if exists or return nan
        def get_df_value(df, index):
            try:
                value = df.iloc[index]
                return value if isinstance(value, float) else np.nan
            except IndexError:
                return np.nan

        for _, company in enumerate(self.datastore.get_companies()):
            data = {
                'company': company.name,
                'share_price': company.actual_share_price,
                'sales': company.sales,
                'curr_assets': company.current_assets,
                'curr_liab': company.current_liabilities,
                'long_term_debts': company.financial_debts,
                'nb_shares': company.nb_shares_issued,
                'equity': company.equity,
                'intangible_assets': company.intangible_assets
            }

            # Dynamically add the 'Net income', 'Dividends' and 'net EPS' fields based on the available data
            for i in range(10):  # Assuming you want to handle up to 10 years
                net_income_value = get_df_value(company.net_income, i)
                data[f'Net income {i + 1} year'] = net_income_value

                dividend_value = get_df_value(company.dividends, i)
                data[f'Dividends {i + 1} year'] = dividend_value

                n_eps_value = get_df_value(company.net_earning_per_share, i)
                data[f'Net earnings per share {i + 1} year'] = n_eps_value
            # End for i

            if rule_df.empty:
                rule_df = pd.DataFrame(data, index=[0])
            else:
                curr_df = pd.DataFrame(data, index=[0])
                rule_df = pd.concat([rule_df, curr_df], axis=0, ignore_index=True)
        # End for _, company
        rule_df.reset_index(inplace=True)
        
        return rule_df
    # End def as_rule_dataframe
    
    # ===========================================================================
    # Private methods
    # ===========================================================================    

    def _detect_encoding(self, file_path: str | Path) -> str:
        """Determine the encoding of a file

        Args:
            file_path (str | Path): path of the json file with all tickers

        Returns:
            str: encoding of the file
        """
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            return result['encoding']
    # End def detect_encoding

    def _read_dict_from_file(self, filename: str | Path) -> dict:
        """Returns the json data under a dictionnary format

        Args:
            filename (str | Path): Path to load the file 

        Returns:
            dict: Dictionnary with ticker as key and name of the company as the value
        """
        encoding = self._detect_encoding(filename)
        with open(filename, 'r', encoding=encoding) as file:
            content = file.read()
            dictionary = json.loads(content)
            return dictionary
    # End def _read_dict_from_file

# End class StockDataImporter