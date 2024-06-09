# -*- coding: utf-8 -*- #
"""
Importer of data
"""
import os
import json
import numpy
import pandas as pd
from polygon import RESTClient
import yfinance as yf

class StockDataImporter:
    """Import the data from Internet"""

    def __init__(self) -> None:
        self.client = RESTClient()
    # End def __init__

    # ===========================================================================
    # Public methods
    # ===========================================================================

    def retrieve_data(self):
        tickers = ['TTE.PA', 'MC.PA', 'SU.PA', 'AI.PA']
        tickers = [yf.Ticker(ticker) for ticker in tickers]

        dfs = {}
        for ticker in tickers:

            # Filter by exchange / market place
            exchanges = ['PAR']
            if ticker.fast_info.exchange in exchanges: 
                # Get financial data
                dfs['ISIN'] = ticker.isin
                dfs['share'] = ticker.fast_info.last_price
                dfs['market_cap'] = ticker.fast_info.market_cap
                dfs['nb_shares'] = ticker.fast_info.shares 
                dfs['dividends'] = ticker.dividends 
                dfs['financials'] = ticker.financials 
                # dfs['balance_sheet'] = ticker.balancesheet 
                dfs['exchange'] = ticker.fast_info.exchange 
                print(ticker.balancesheet.index)
            
            actions = ticker.actions
            isin = ticker.isin
            cf = ticker.cashflow
            print(f'\n---------------- {ticker.ticker} ----------------')
            # print(f'Data:\n{dfs}')
            # print(f'Share:\n {share}')
            # print(f'ISIN: {isin}')
            # print(f'Cashflow:\n {cf}')


            # Concat in one dataframe
            # fs = pd.concat([share, isin, cf])

            # data = fs.T
            # data = data.reset_index()
            # data.columns = ['Date', *data.columns[1:]]
            # data['Ticker'] = ticker.ticker
            # dfs.append(data)
        
            # print(fs)
    # End def retrieve_data

    # ===========================================================================
    # Private methods
    # ===========================================================================

# End class StockDataImporter