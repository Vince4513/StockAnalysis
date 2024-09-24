# -*- coding: utf-8 -*- #
"""
Importer of data
"""

from __future__ import annotations

import ast
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
                    print(f"\n{ticker.ticker}", end='\r') #{dir(ticker)}
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
# End class StockDataImporter