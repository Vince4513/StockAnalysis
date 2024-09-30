# -*- coding: utf-8 -*- #
"""
Main file calling classes 
"""
import sys
import logging 
import numpy as np
import pandas as pd

from interface.webapp import StockAnalysisApp
    
def main():
    db_path=r'C:\diskD\6 - CODE\stock_analysis\stock_analysis\company.db'
    tickers_path=r'C:\diskD\6 - CODE\stock_analysis\stock_analysis\yh_tickers.json' 
    # logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    app = StockAnalysisApp(db_path, tickers_path)
    app.run()


if __name__ == "__main__":
    main()