# -*- coding: utf-8 -*- #
"""
Importer of data
"""

from __future__ import annotations

import os
import json
import logging
import chardet
import yfinance as yf

from typing import List
from pathlib import Path
from curl_cffi import requests
from concurrent.futures import ThreadPoolExecutor


# ===========================================================================
# Constant and global variables
# ===========================================================================

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ===========================================================================
# FinancialDataImporter Class
# ===========================================================================

class FinancialDataImporter:
    """Import the data from Internet"""

    def __init__(self, ticker_source=None, data_path="data/raw/"):
        self.ticker_source = ticker_source or "data/raw/yh_tickers.json"
        self.data_path = data_path
        os.makedirs(self.data_path, exist_ok=True)
    # End def __init__

    # ===========================================================================
    # Public methods
    # ===========================================================================

    def retrieve_tickers(self) -> List[str]:
        """Load tickers from file or return a fallback list."""
        if not os.path.exists(self.ticker_source):
            logger.info(f"[!] Ticker file not found: {self.ticker_source}")
            return ["TTE.PA", "AI.PA", "SAN.PA", "DG.PA", "OR.PA", "SU.PA"]
        
        data = self._read_dict_from_file(self.ticker_source)
        tickers = list(data.keys()) if data else []
        logger.info(f"[+] Retrieved {len(tickers)} tickers")
        return tickers
    # End def retrieve_tickers
                
    def retrieve_data(self, tickers: List[str] = None):
        """Sequential download of financials."""
        tickers = tickers or self.retrieve_tickers()

        for ticker in tickers:
            self._fetch_ticker_data(ticker)
    # End def retrieve_data

    def parallel_retrieve_data(self, tickers: List[str] = None, max_workers=2):
        """Parallel download using threads."""
        tickers = tickers or self.retrieve_tickers()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(self._fetch_ticker_data, tickers)
    # End def parallel_retrieve_data

    # ===========================================================================
    # Private methods
    # ===========================================================================    

    def _detect_encoding(self, filepath: str) -> str:
        """Detect file encoding using chardet."""
        with open(filepath, "rb") as f:
            raw_data = f.read(10000)
        
        return chardet.detect(raw_data)["encoding"]
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
    
    def _fetch_ticker_data(self, ticker: str):
        """Fetch and store raw financials for one ticker."""
        try:
            session = requests.Session(impersonate="chrome")
            ticker_data = yf.Ticker(ticker, session=session)
            data = ticker_data.info
            data['isin'] = ticker_data.isin
            data['incomestmt'] = self._convert_timestamp(ticker_data.incomestmt.to_dict(orient='index'))
            data['balancesheet'] = self._convert_timestamp(ticker_data.balancesheet.to_dict(orient='index'))
            dividends = {ts.strftime('%Y-%m-%d'): val for ts, val in ticker_data.dividends.items()}
            data['dividends'] = dividends

            output_path = os.path.join(self.data_path, f"{ticker}.json")
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            logger.info(f"[✓] Downloaded {ticker}")

        except Exception as e:
            logger.error(f"[✗] Error downloading {ticker}: {e}")
    # End def _fetch_ticker_data

    def _convert_timestamp(self, original_dict: dict) -> dict:
        # Convert the dictionary
        json_ready_dict = {
            key: {ts.strftime('%Y-%m-%d'): value for ts, value in subdict.items()}
            for key, subdict in original_dict.items()
        }
        return json_ready_dict
    # End def _convert_timestamp
# End class StockDataImporter


if __name__ == '__main__':
    i = FinancialDataImporter(ticker_source="yh.json")
    logger.debug(f"Ticker source: {i.ticker_source}")
    logger.debug(f"Data path: {i.data_path}")

    # i.retrieve_tickers()
    i.parallel_retrieve_data(["TTE.PA", "AI.PA", "SAN.PA", "DG.PA", "OR.PA", "SU.PA"], max_workers=1)
